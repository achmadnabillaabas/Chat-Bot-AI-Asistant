"""
Documents API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func
import logging
import os
import shutil
from pathlib import Path
from datetime import datetime

from app.core.database import get_db
from app.core.config import settings
from app.schemas.document import (
    DocumentResponse,
    DocumentListResponse,
    DocumentUploadResponse
)
from app.models.knowledge_base import KnowledgeBase, Document, DocumentChunk, ProcessingStatus
from app.models.user import User
from app.services.document_processor import document_processor
from app.services.embedding_service import embedding_service
from app.services.qdrant_service import qdrant_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/knowledge-bases", tags=["documents"])

# Allowed file extensions
ALLOWED_EXTENSIONS = {"pdf", "docx", "txt", "md", "csv"}
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB


def get_default_user(db: Session) -> User:
    """Get default user."""
    user = db.query(User).filter(User.email == "demo@aiassistant.local").first()
    if not user:
        user = User(
            email="demo@aiassistant.local",
            username="demo_user",
            hashed_password="demo",
            full_name="Demo User",
            role="user",
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def get_file_extension(filename: str) -> str:
    """Get file extension without dot."""
    return filename.rsplit(".", 1)[1].lower() if "." in filename else ""


async def process_document_async(document_id: int, db: Session):
    """
    Process document: extract, chunk, embed, and index.
    This is a simplified synchronous version. In production, use background tasks.
    """
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        return
    
    kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == doc.knowledge_base_id).first()
    if not kb:
        return
    
    try:
        # EXTRACT
        doc.status = ProcessingStatus.EXTRACTING
        db.commit()
        
        text = document_processor.extract_text(doc.file_path, doc.file_type)
        
        if not text or not text.strip():
            raise Exception("No text extracted from document")
        
        # CLEAN
        text = document_processor.clean_text(text)
        
        # CHUNK
        doc.status = ProcessingStatus.CHUNKING
        db.commit()
        
        chunks = document_processor.chunk_text(text, doc.file_type)
        
        if not chunks:
            raise Exception("No chunks generated")
        
        # EMBED
        doc.status = ProcessingStatus.EMBEDDING
        db.commit()
        
        # Extract text from chunks for embedding
        chunk_texts = [chunk.text for chunk in chunks]
        embeddings = await embedding_service.generate_embeddings(chunk_texts)
        
        if len(embeddings) != len(chunks):
            raise Exception("Embedding count mismatch")
        
        # INDEX
        doc.status = ProcessingStatus.INDEXING
        db.commit()
        
        # Prepare vectors and payloads for Qdrant
        vectors = []
        payloads = []
        
        for chunk, embedding in zip(chunks, embeddings):
            vectors.append(embedding)
            payloads.append({
                "knowledge_base_id": kb.id,
                "document_id": doc.id,
                "document_name": doc.filename,
                "chunk_index": chunk.chunk_index,
                "page_number": chunk.page_number,
                "text": chunk.text
            })
        
        # Upsert to Qdrant
        vector_ids = qdrant_service.upsert_vectors(
            collection_name=kb.collection_name,
            vectors=vectors,
            payloads=payloads
        )
        
        # Save chunks to database
        for chunk, vector_id in zip(chunks, vector_ids):
            db_chunk = DocumentChunk(
                document_id=doc.id,
                chunk_index=chunk.chunk_index,
                content=chunk.text,
                page_number=chunk.page_number,
                char_count=chunk.char_count,
                vector_id=vector_id
            )
            db.add(db_chunk)
        
        # Update document
        doc.status = ProcessingStatus.READY
        doc.chunk_count = len(chunks)
        doc.processed_at = datetime.utcnow()
        doc.error_message = None
        db.commit()
        
        logger.info(f"Document processed successfully | id={doc.id} | chunks={len(chunks)}")
        
    except Exception as e:
        logger.error(f"Document processing failed | id={doc.id} | error={str(e)}")
        doc.status = ProcessingStatus.FAILED
        doc.error_message = str(e)
        db.commit()


@router.get("/{kb_id}/documents", response_model=DocumentListResponse)
async def list_documents(
    kb_id: int,
    db: Session = Depends(get_db)
):
    """
    List all documents in a knowledge base.
    """
    user = get_default_user(db)
    
    # Check KB ownership
    kb = db.query(KnowledgeBase).filter(
        KnowledgeBase.id == kb_id,
        KnowledgeBase.user_id == user.id
    ).first()
    
    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge base not found"
        )
    
    documents = db.query(Document).filter(
        Document.knowledge_base_id == kb_id
    ).order_by(
        Document.uploaded_at.desc()
    ).all()
    
    items = [
        DocumentResponse(
            id=doc.id,
            knowledge_base_id=doc.knowledge_base_id,
            filename=doc.filename,
            file_type=doc.file_type,
            file_size=doc.file_size,
            status=doc.status.value,
            error_message=doc.error_message,
            chunk_count=doc.chunk_count,
            uploaded_at=doc.uploaded_at,
            processed_at=doc.processed_at
        )
        for doc in documents
    ]
    
    return DocumentListResponse(
        items=items,
        total=len(items)
    )


@router.post("/{kb_id}/documents", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    kb_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a document to a knowledge base.
    """
    user = get_default_user(db)
    
    # Check KB ownership
    kb = db.query(KnowledgeBase).filter(
        KnowledgeBase.id == kb_id,
        KnowledgeBase.user_id == user.id
    ).first()
    
    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge base not found"
        )
    
    # Validate file extension
    file_ext = get_file_extension(file.filename)
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not supported. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Validate file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / (1024*1024):.0f}MB"
        )
    
    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is empty"
        )
    
    # Create upload directory if not exists
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    import uuid
    unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
    file_path = upload_dir / unique_filename
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        logger.error(f"Failed to save file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save file"
        )
    
    # Create document record
    doc = Document(
        knowledge_base_id=kb_id,
        filename=file.filename,
        file_path=str(file_path),
        file_type=file_ext,
        file_size=file_size,
        status=ProcessingStatus.UPLOADING
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    
    logger.info(f"Document uploaded | id={doc.id} | filename={file.filename}")
    
    # Process document asynchronously
    # In production, use background tasks (FastAPI BackgroundTasks or Celery)
    try:
        await process_document_async(doc.id, db)
    except Exception as e:
        logger.error(f"Document processing error: {str(e)}")
    
    # Refresh to get updated status
    db.refresh(doc)
    
    return DocumentUploadResponse(
        id=doc.id,
        filename=doc.filename,
        status=doc.status.value,
        message="Document uploaded and processing started"
    )


@router.delete("/{kb_id}/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    kb_id: int,
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a document.
    """
    user = get_default_user(db)
    
    # Check KB ownership
    kb = db.query(KnowledgeBase).filter(
        KnowledgeBase.id == kb_id,
        KnowledgeBase.user_id == user.id
    ).first()
    
    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge base not found"
        )
    
    doc = db.query(Document).filter(
        Document.id == document_id,
        Document.knowledge_base_id == kb_id
    ).first()
    
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Delete Qdrant vectors
    try:
        qdrant_service.delete_vectors(
            collection_name=kb.collection_name,
            filters={"document_id": document_id}
        )
    except Exception as e:
        logger.error(f"Failed to delete Qdrant vectors: {str(e)}")
    
    # Delete file
    try:
        if os.path.exists(doc.file_path):
            os.remove(doc.file_path)
    except Exception as e:
        logger.error(f"Failed to delete file: {str(e)}")
    
    # Delete from database (cascades to chunks)
    db.delete(doc)
    db.commit()
    
    logger.info(f"Document deleted | id={document_id}")
    
    return None


@router.post("/{kb_id}/documents/{document_id}/reindex", response_model=DocumentResponse)
async def reindex_document(
    kb_id: int,
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Reindex a document.
    """
    user = get_default_user(db)
    
    # Check KB ownership
    kb = db.query(KnowledgeBase).filter(
        KnowledgeBase.id == kb_id,
        KnowledgeBase.user_id == user.id
    ).first()
    
    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge base not found"
        )
    
    doc = db.query(Document).filter(
        Document.id == document_id,
        Document.knowledge_base_id == kb_id
    ).first()
    
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Delete existing chunks and vectors
    try:
        qdrant_service.delete_vectors(
            collection_name=kb.collection_name,
            filters={"document_id": document_id}
        )
    except Exception as e:
        logger.error(f"Failed to delete old vectors: {str(e)}")
    
    # Delete chunks from database
    db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).delete()
    db.commit()
    
    # Reset document status
    doc.status = ProcessingStatus.UPLOADING
    doc.chunk_count = 0
    doc.error_message = None
    doc.processed_at = None
    db.commit()
    
    # Reprocess
    try:
        await process_document_async(doc.id, db)
    except Exception as e:
        logger.error(f"Document reprocessing error: {str(e)}")
    
    db.refresh(doc)
    
    return DocumentResponse(
        id=doc.id,
        knowledge_base_id=doc.knowledge_base_id,
        filename=doc.filename,
        file_type=doc.file_type,
        file_size=doc.file_size,
        status=doc.status.value,
        error_message=doc.error_message,
        chunk_count=doc.chunk_count,
        uploaded_at=doc.uploaded_at,
        processed_at=doc.processed_at
    )
