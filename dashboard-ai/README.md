# AI Assistant Dashboard

Enterprise AI workspace with ChatGPT-like experience, featuring Custom RAG, Token Usage Analytics, Model Management via 9Router, and Telegram Bot integration.

## Features

- 🤖 **AI Combo Selection** via 9Router (AI General, AI Coding, AI Fast)
- 💬 **Smart Chat Interface** with Markdown support and conversation history
- 📚 **Custom RAG** with knowledge base management and Qdrant vector search (Phase 7+)
- 📊 **Token Usage Analytics** with detailed tracking and cost estimation (Phase 4+)
- 📱 **Telegram Bot** integration (Phase 5+)
- 🎨 **Syntactic Slate Design System** - professional, utility-focused interface

### Why Combos?

The application uses **9Router Combos** instead of exposing individual models:
- Users choose by purpose (general, coding, fast) not by model
- 9Router handles all model routing, provider selection, and fallback
- No provider lock-in - works with any AI provider 9Router supports
- Better reliability with automatic fallback
- See `docs/COMBO_ARCHITECTURE.md` for details

## Tech Stack

### Frontend
- Next.js 14+ (React)
- TypeScript
- Tailwind CSS with custom design tokens
- Inter & JetBrains Mono fonts

### Backend
- Python 3.11+
- FastAPI
- PostgreSQL (relational data)
- Qdrant (vector database)
- python-telegram-bot

## Project Structure

```
ai-assistant-dashboard/
├── frontend/               # Next.js application
│   ├── src/
│   │   ├── app/           # Next.js App Router
│   │   ├── components/    # React components
│   │   ├── lib/           # Utilities and API clients
│   │   └── styles/        # Global styles
│   └── public/
├── backend/               # FastAPI application
│   ├── app/
│   │   ├── api/           # API routes
│   │   ├── services/      # Business logic
│   │   ├── models/        # Database models
│   │   ├── schemas/       # Pydantic schemas
│   │   └── core/          # Configuration
│   └── alembic/           # Database migrations
└── docs/                  # Documentation
```

## Getting Started

### Prerequisites

- Node.js 18+ and npm/yarn
- Python 3.11+
- PostgreSQL 14+
- Qdrant (Docker or cloud)
- 9Router API key

### Installation

1. **Clone the repository**

```bash
git clone <repository-url>
cd ai-assistant-dashboard
```

2. **Set up environment variables**

```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Frontend Setup**

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:3000`

**Test Responsive Behavior:**
```bash
# After starting the dev server, test these viewport sizes:
# - 360px (narrow mobile)
# - 768px (tablet - drawer becomes fixed sidebar)
# - 1024px+ (desktop)
# 
# Mobile: Hamburger opens drawer overlay
# Desktop: Hamburger collapses/expands sidebar
```

4. **Backend Setup**

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend runs at `http://localhost:8000`

5. **Database Setup**

```bash
cd backend
alembic upgrade head
```

6. **Qdrant Setup**

```bash
docker run -p 6333:6333 qdrant/qdrant
```

## Development Phases

This project is implemented in phases as outlined in the PRD:

- ✅ **Phase 1: Project setup + database** (COMPLETE)
- ✅ **Phase 1.5: UI Refinement** (COMPLETE - Responsive layout fully implemented)
- ✅ **Phase 2: 9Router + basic AI chat** (COMPLETE - Full end-to-end chat working)
- ⬜ Phase 3: Enhanced Chat UI + conversation history
- ⬜ Phase 4: Token tracking + analytics dashboard
- ⬜ Phase 5: Telegram Bot
- ⬜ Phase 6: Document upload
- ⬜ Phase 7: RAG + Qdrant
- ⬜ Phase 8: RAG integration to Dashboard and Telegram
- ⬜ Phase 9: Authentication + roles + security
- ⬜ Phase 10: UI/UX refinement + deployment

### Recent Updates

**Phase 2 Complete:**
- ✅ 9Router integration with AI Combos
- ✅ Combo discovery (GET /api/combos)
- ✅ POST /api/chat endpoint with combo selection
- ✅ Conversation persistence (database)
- ✅ Message history
- ✅ Token usage tracking (input, output, total)
- ✅ Frontend chat interface with Markdown support
- ✅ AI Combo selector in chat UI
- ✅ Error handling and loading states
- ✅ Real-time AI responses
- ✅ New chat functionality
- ✅ Fallback combos when 9Router unavailable

**Quick Start:**
See `QUICKSTART_PHASE2.md` for 5-minute setup guide.

## Design System

This application follows the **Syntactic Slate** design system:

- Professional, utility-focused interface
- Dark slate color palette (#0B0F17 base)
- Inter for UI, JetBrains Mono for technical data
- Minimal shadows, crisp borders
- 8px baseline grid
- No AI slop: no excessive gradients, glows, or glassmorphism

See `design/stitch_ai_assistant_dashboard/syntactic_slate/DESIGN.md` for complete specifications.

## API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## License

[Your License Here]
