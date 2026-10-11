# AI Combo Architecture

## Overview

The AI Assistant Dashboard uses **9Router Combos** for AI model selection instead of exposing individual models to end users. This architecture delegates all model routing, provider selection, and fallback logic to 9Router.

---

## What is a Combo?

A **Combo** is a pre-configured routing strategy managed by 9Router that:
- Selects appropriate AI models based on request type
- Routes requests to multiple providers (Anthropic, OpenAI, Google, etc.)
- Handles fallback when a provider is unavailable
- Manages API credentials for all providers
- Optimizes for cost, speed, or quality based on configuration

**Our application only selects which Combo to use.** 9Router handles everything else.

---

## Architecture

```
User Interface
      ↓
  AI Combo Selector
  (ai-general, ai-coding, ai-fast)
      ↓
  Frontend → Backend
      ↓
  9Router API
  (with combo ID)
      ↓
  9Router Intelligence Layer
  - Selects best model
  - Chooses provider
  - Handles fallback
  - Manages credentials
      ↓
  AI Provider
  (Claude, GPT, Gemini, etc.)
```

---

## User Mental Model

### What Users See:
- **AI Combo dropdown** with options like:
  - AI General
  - AI Coding
  - AI Fast
  - AI Research

### What Users DON'T See:
- Individual models (Claude 3.5 Sonnet, GPT-4, etc.)
- Providers (Anthropic, OpenAI, Google)
- Routing logic
- Fallback chains
- API credentials

---

## API Changes

### Before (Individual Models)
```
GET /api/models
Response:
[
  {"id": "claude-3-5-sonnet", "name": "Claude 3.5 Sonnet", "provider": "anthropic"},
  {"id": "gpt-4o", "name": "GPT-4o", "provider": "openai"}
]
```

### After (Combos Only)
```
GET /api/combos
Response:
[
  {"id": "ai-general", "name": "AI General", "type": "combo"},
  {"id": "ai-coding", "name": "AI Coding", "type": "combo"}
]
```

---

## Chat Request Flow

### 1. User Selects Combo
User picks "AI General" from dropdown.

### 2. Frontend Sends Combo ID
```typescript
chatApi.sendMessage({
  message: "Hello",
  model: "ai-general",  // Exact combo ID, unchanged
  conversation_id: 123
})
```

### 3. Backend Forwards to 9Router
```python
await ninerouter_service.chat_completion(
    messages=[{"role": "user", "content": "Hello"}],
    model="ai-general"  # Exact combo ID
)
```

### 4. 9Router Routes Request
9Router receives `model: "ai-general"` and:
- Determines best model (e.g., Claude 3.5 Sonnet)
- Selects provider (e.g., Anthropic)
- If Anthropic fails, tries fallback (e.g., OpenAI GPT-4)
- Returns response with usage data

### 5. Backend Saves & Returns
```python
# Save to database
token_usage = TokenUsage(
    model="ai-general",  # Combo ID
    input_tokens=120,
    output_tokens=75,
    ...
)
```

---

## Combo Discovery

### Backend Service
```python
async def list_combos(self) -> List[Dict[str, Any]]:
    """
    Fetch available combos from 9Router.
    
    Filters models list to include only combo-style identifiers.
    Falls back to default combos if API unavailable.
    """
    response = await client.get(f"{base_url}/v1/models")
    models = response.json()["data"]
    
    # Filter for combos (e.g., IDs starting with "ai-")
    combos = [
        {
            "id": m["id"],
            "name": format_name(m["id"]),
            "type": "combo"
        }
        for m in models
        if m["id"].startswith("ai-") or "combo" in m["id"].lower()
    ]
    
    return combos or default_combos
```

### Default Fallback Combos
If 9Router is unavailable:
```python
[
    {"id": "ai-general", "name": "AI General", "type": "combo"},
    {"id": "ai-coding", "name": "AI Coding", "type": "combo"},
    {"id": "ai-fast", "name": "AI Fast", "type": "combo"}
]
```

---

## UI Implementation

### Chat Header
```tsx
<div className="flex items-center gap-2">
  <span className="font-label-md text-label-md text-on-surface-variant">
    AI Combo:
  </span>
  <select
    value={selectedCombo}
    onChange={(e) => setSelectedCombo(e.target.value)}
    className="..."
  >
    {combos.map(combo => (
      <option key={combo.id} value={combo.id}>
        {combo.name}
      </option>
    ))}
  </select>
</div>
```

### Empty State
If no combos available:
```
No AI Combo configured yet.
Please configure AI Combos to start chatting.
```

### Error Handling
If combo fails:
```
AI Combo is currently unavailable.
Please try again or select another Combo.

[Retry] [Select Another Combo]
```

---

## Token Analytics

Token tracking remains unchanged:
- **Combo ID** is stored as the `model` field
- Input/output/total tokens from 9Router
- If 9Router returns actual model used, it can be stored separately
- Analytics can show usage by combo

Example database record:
```sql
INSERT INTO token_usage (
    model,           -- "ai-general" (combo ID)
    input_tokens,    -- 120
    output_tokens,   -- 75
    total_tokens,    -- 195
    ...
)
```

---

## Configuration

### Environment Variables
```bash
# Use combo ID as default
DEFAULT_MODEL=ai-general

# Not used anymore:
# DEFAULT_MODEL=claude-3-5-sonnet  ❌
```

### 9Router Setup
No application-side configuration needed.
All combo definitions live in 9Router:
- Model selection rules
- Provider priorities
- Fallback chains
- Cost/speed/quality optimization

---

## Benefits

### For Users
- **Simpler mental model**: Choose by purpose (general, coding, fast)
- **No provider lock-in**: 9Router handles providers transparently
- **Better reliability**: Automatic fallback if provider fails
- **Optimized performance**: 9Router picks best model for each request

### For Application
- **Less complexity**: No model routing logic
- **No credential management**: 9Router handles API keys
- **Easier maintenance**: Update combos in 9Router, not code
- **Better abstraction**: Focus on features, not infrastructure

### For 9Router
- **Full control**: Manages routing strategy
- **Can optimize**: Cost, speed, quality based on usage
- **Provider flexibility**: Add/remove providers without app changes
- **A/B testing**: Test model combinations without frontend changes

---

## Migration from Individual Models

### What Changed
1. ✅ API endpoint: `/api/models` → `/api/combos`
2. ✅ Schema: `ModelInfo` → `ComboInfo`
3. ✅ UI label: "Model" → "AI Combo"
4. ✅ Default value: `claude-3-5-sonnet` → `ai-general`
5. ✅ Service method: `list_models()` → `list_combos()`
6. ✅ Frontend API: `modelsApi` → `combosApi`

### What Stayed the Same
- ✅ Chat API endpoint: `POST /api/chat`
- ✅ Request format: `{message, model, conversation_id}`
- ✅ Token usage tracking
- ✅ Conversation persistence
- ✅ Error handling
- ✅ UI layout and design

---

## Testing

### Verify Combo Selection
1. Start backend and frontend
2. Visit http://localhost:3000/chat
3. Check "AI Combo:" dropdown
4. Should see combo names (AI General, etc.)
5. Should NOT see individual models (Claude, GPT, etc.)

### Verify Chat Works
1. Select a combo
2. Send message
3. Verify response appears
4. Check token usage displayed
5. Verify combo ID saved in database

### Verify Fallback
If no combos available:
- Should see "No AI Combo configured yet"
- Send button should be disabled
- Should not crash

---

## Future Enhancements

### Admin Panel (Phase 9+)
Advanced users could:
- View combo definitions
- See which models each combo uses
- Monitor provider health
- Configure custom combos

But regular users only see:
- **AI Combo selector**
- **No individual model management**

---

## Summary

**Key Principle:**  
The application is a **Combo Consumer**, not a **Model Manager**.

**Responsibility Split:**
- **Our App**: Select which combo to use
- **9Router**: Everything else (models, providers, routing, fallback)

**User Experience:**
- Simple: Choose purpose (general, coding, fast)
- Reliable: Automatic fallback
- Transparent: Don't worry about providers

**Status:** ✅ Implemented and tested
