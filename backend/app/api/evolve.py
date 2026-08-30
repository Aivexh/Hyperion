import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.hyperagent.meta_agent import meta_agent_mutator
from app.hyperagent.archive import archive_manager

router = APIRouter(tags=["Evolution"])

@router.post("/evolve/trigger")
async def trigger_evolution():
    """
    Triggers a new HyperAgent self-improvement evolution generation.
    Streams live progress logs and resulting generation details via Server-Sent Events (SSE).
    """
    async def event_generator():
        async for event in meta_agent_mutator.evolve_next_generation():
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.get("/evolve/status")
async def get_evolution_status():
    """Returns status summary of current generations archive."""
    latest = archive_manager.get_latest_generation()
    all_gens = archive_manager.get_all_generations()
    return {
        "total_generations": len(all_gens),
        "latest_generation_id": latest.generation_id,
        "latest_score": latest.score,
        "baseline_score": all_gens[0].score,
        "improvement_delta": round(latest.score - all_gens[0].score, 1)
    }
