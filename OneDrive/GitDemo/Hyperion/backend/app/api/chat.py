import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional

from app.hyperagent.task_agent import TaskAgentExecutor

router = APIRouter(tags=["Chat"])

class ChatRequest(BaseModel):
    query: str
    generation_id: Optional[str] = None

@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    SSE Streaming Chat Endpoint.
    Executes TaskAgent ReAct loop with prompt/code heuristics loaded from generation_id.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query string cannot be empty.")

    executor = TaskAgentExecutor(generation_id=request.generation_id)

    async def event_generator():
        async for event in executor.execute_stream(request.query):
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
