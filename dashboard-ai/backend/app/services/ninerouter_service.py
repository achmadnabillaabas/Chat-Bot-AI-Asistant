"""
9Router service for AI model requests.
"""
import httpx
import logging
from typing import Dict, List, Any, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)


class NineRouterService:
    """Service for interacting with 9Router AI Gateway."""
    
    def __init__(self):
        self.base_url = settings.NINEROUTER_BASE_URL
        self.api_key = settings.NINEROUTER_API_KEY
        self.default_model = settings.DEFAULT_MODEL
        self.timeout = 120.0  # 2 minutes for AI requests
        
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for 9Router API requests."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Send chat completion request to 9Router.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model name (uses default if not specified)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Response dict containing 'content', 'model', and 'usage'
            
        Raises:
            httpx.HTTPError: If request fails
        """
        model = model or self.default_model
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        # Safe debug logging (no secrets)
        target_url = f"{self.base_url}/v1/chat/completions"
        logger.info(
            f"9Router Chat Request | "
            f"url={target_url} | "
            f"model={model} | "
            f"messages={len(messages)} | "
            f"temperature={temperature}"
        )
        
        try:
            import time
            start_time = time.time()
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    target_url,
                    headers=self._get_headers(),
                    json=payload
                )
                
                duration_ms = int((time.time() - start_time) * 1000)
                
                # Log response status
                logger.info(
                    f"9Router Response | "
                    f"status={response.status_code} | "
                    f"duration={duration_ms}ms"
                )
                
                # If error, log safe details before raising
                if response.status_code >= 400:
                    try:
                        error_body = response.json()
                        logger.error(
                            f"9Router Error Response | "
                            f"status={response.status_code} | "
                            f"error={error_body.get('error', {}).get('message', 'Unknown')} | "
                            f"type={error_body.get('error', {}).get('type', 'Unknown')}"
                        )
                    except:
                        logger.error(
                            f"9Router Error Response | "
                            f"status={response.status_code} | "
                            f"body={response.text[:500]}"
                        )
                
                response.raise_for_status()
                data = response.json()
                
                # Extract response
                choice = data.get("choices", [{}])[0]
                message = choice.get("message", {})
                content = message.get("content", "")
                
                # Extract usage
                usage = data.get("usage", {})
                
                result = {
                    "content": content,
                    "model": data.get("model", model),
                    "usage": {
                        "input_tokens": usage.get("prompt_tokens", 0),
                        "output_tokens": usage.get("completion_tokens", 0),
                        "total_tokens": usage.get("total_tokens", 0)
                    }
                }
                
                logger.info(
                    f"9Router response received | "
                    f"model={result['model']} | "
                    f"tokens={result['usage']['total_tokens']}"
                )
                
                return result
                
        except httpx.HTTPStatusError as e:
            # Enhanced error logging with sanitized details
            error_detail = "Unknown error"
            error_type = "http_error"
            
            try:
                error_body = e.response.json()
                error_detail = error_body.get("error", {}).get("message", str(error_body))
                error_type = error_body.get("error", {}).get("type", "http_error")
            except:
                error_detail = e.response.text[:500] if e.response.text else "No response body"
            
            logger.error(
                f"9Router HTTP Error | "
                f"status={e.response.status_code} | "
                f"type={error_type} | "
                f"detail={error_detail}"
            )
            
            # Re-raise with context
            raise httpx.HTTPStatusError(
                f"9Router returned {e.response.status_code}: {error_detail}",
                request=e.request,
                response=e.response
            )
            
        except httpx.TimeoutException as e:
            logger.error(f"9Router request timeout after {self.timeout}s")
            raise
            
        except httpx.RequestError as e:
            logger.error(f"9Router request error: {type(e).__name__} | {str(e)}")
            raise
            
        except Exception as e:
            logger.error(f"9Router unexpected error: {type(e).__name__} | {str(e)}", exc_info=True)
            raise
    
    async def list_combos(self) -> List[Dict[str, Any]]:
        """
        List available AI Combos from 9Router.
        
        Returns:
            List of combo dicts with 'id', 'name', 'type'
            
        Raises:
            httpx.HTTPError: If request fails
        """
        logger.info("Fetching AI Combos from 9Router")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/v1/models",
                    headers=self._get_headers()
                )
                response.raise_for_status()
                data = response.json()
                
                models = data.get("data", [])
                
                # Filter for combos only (models that start with "ai-" or contain "combo")
                # Adjust this filter based on actual 9Router combo naming convention
                result = []
                for model in models:
                    model_id = model.get("id", "")
                    # Filter for combo-style models
                    if model_id.startswith("ai-") or "combo" in model_id.lower():
                        # Clean up the name for display
                        name = model_id.replace("ai-", "AI ").replace("-", " ").title()
                        result.append({
                            "id": model_id,
                            "name": name,
                            "type": "combo"
                        })
                
                # If no combos found, provide default combos
                if not result:
                    result = [
                        {"id": "ai-general", "name": "AI General", "type": "combo"},
                        {"id": "ai-coding", "name": "AI Coding", "type": "combo"},
                        {"id": "ai-fast", "name": "AI Fast", "type": "combo"},
                    ]
                
                logger.info(f"Retrieved {len(result)} AI Combos from 9Router")
                return result
                
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch combos from 9Router: {str(e)}")
            # Return default combos as fallback
            return [
                {"id": "ai-general", "name": "AI General", "type": "combo"},
                {"id": "ai-coding", "name": "AI Coding", "type": "combo"},
                {"id": "ai-fast", "name": "AI Fast", "type": "combo"},
            ]
    
    async def health_check(self) -> bool:
        """
        Check if 9Router is accessible.
        
        Returns:
            True if 9Router is accessible, False otherwise
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/v1/models",
                    headers=self._get_headers()
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"9Router health check failed: {str(e)}")
            return False


# Singleton instance
ninerouter_service = NineRouterService()
