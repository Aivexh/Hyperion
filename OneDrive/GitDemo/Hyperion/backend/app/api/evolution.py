import difflib
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional

from app.hyperagent.archive import archive_manager, Generation

router = APIRouter(tags=["Evolution History"])

@router.get("/evolution/history")
async def get_evolution_history() -> List[Dict[str, Any]]:
    """Returns the full list of generations with metadata and evaluation metrics."""
    generations = archive_manager.get_all_generations()
    return [gen.model_dump() for gen in generations]

@router.get("/generations/{gen_id}")
async def get_generation_by_id(gen_id: str) -> Dict[str, Any]:
    """Returns details for a specific generation by ID."""
    gen = archive_manager.get_generation(gen_id)
    if not gen:
        raise HTTPException(status_code=404, detail=f"Generation '{gen_id}' not found.")
    return gen.model_dump()

@router.get("/evolution/diff")
async def get_generation_diff(
    gen_a: str = Query(..., description="Base generation ID (e.g. gen_0)"),
    gen_b: str = Query(..., description="Target generation ID (e.g. gen_1)")
):
    """Calculates line-by-line diff between two generation prompt templates."""
    g_a = archive_manager.get_generation(gen_a)
    g_b = archive_manager.get_generation(gen_b)

    if not g_a or not g_b:
        raise HTTPException(status_code=404, detail="One or both generation IDs were not found.")

    prompt_a_lines = g_a.prompt.splitlines()
    prompt_b_lines = g_b.prompt.splitlines()

    diff_lines = list(difflib.unified_diff(
        prompt_a_lines,
        prompt_b_lines,
        fromfile=f"Generation {gen_a}",
        tofile=f"Generation {gen_b}",
        lineterm=""
    ))

    return {
        "gen_a": gen_a,
        "gen_b": gen_b,
        "score_a": g_a.score,
        "score_b": g_b.score,
        "score_delta": round(g_b.score - g_a.score, 1),
        "unified_diff": "\n".join(diff_lines),
        "prompt_a": g_a.prompt,
        "prompt_b": g_b.prompt,
        "code_a": g_a.code_mutations,
        "code_b": g_b.code_mutations
    }
