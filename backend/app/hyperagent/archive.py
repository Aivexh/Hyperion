import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from backend.app.config import settings

class Generation(BaseModel):
    generation_id: str
    parent_id: Optional[str] = None
    prompt: str
    code_mutations: str = ""
    score: float = 0.0
    rubric_scores: Dict[str, float] = Field(default_factory=dict)
    evaluation_history: List[Dict[str, Any]] = Field(default_factory=list)
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    token_cost: float = 0.0012
    status: str = "active"
    mutation_notes: str = ""

BASELINE_PROMPT_G0 = """You are a domain-expert AI TaskAgent operating in a ReAct (Reasoning + Acting) execution loop.
When given a user goal:
1. Reason step-by-step about what tools are required.
2. Formulate explicit Action and Action Input using available tools: [web_search, calculator, python_interpreter, data_analyzer].
3. Analyze Observation results thoroughly.
4. Produce a crisp, accurate, structured Final Answer.
"""

class ArchiveManager:
    def __init__(self, archive_path: str = settings.ARCHIVE_PATH):
        self.archive_path = archive_path
        self.generations: Dict[str, Generation] = {}
        self.load_archive()

    def load_archive(self):
        """Loads generations from JSON file or initializes seed generation G0."""
        if os.path.exists(self.archive_path):
            try:
                with open(self.archive_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for key, val in data.get("generations", {}).items():
                        self.generations[key] = Generation(**val)
            except Exception as e:
                print(f"Warning loading archive: {e}. Re-initializing baseline.")
                self._create_seed_generation()
        else:
            self._create_seed_generation()

    def _create_seed_generation(self):
        """Initializes baseline Generation G0."""
        g0 = Generation(
            generation_id="gen_0",
            parent_id=None,
            prompt=BASELINE_PROMPT_G0,
            code_mutations="Standard ReAct loop logic with standard tool bindings.",
            score=62.5,
            rubric_scores={
                "correctness": 24.0,       # Max 40
                "tool_efficiency": 18.0,   # Max 30
                "reasoning_clarity": 14.5, # Max 20
                "speed_cost": 6.0          # Max 10
            },
            evaluation_history=[
                {"task": "Math Equation", "score": 70.0, "status": "PASSED"},
                {"task": "Fact Lookup", "score": 60.0, "status": "PASSED"},
                {"task": "Multi-Step Logic", "score": 57.5, "status": "PARTIAL"}
            ],
            token_cost=0.0015,
            status="active",
            mutation_notes="Baseline seed generation G0 created."
        )
        self.generations["gen_0"] = g0
        self.save_archive()

    def save_archive(self):
        """Persists generations archive to JSON."""
        data = {
            "generations": {gid: gen.model_dump() for gid, gen in self.generations.items()},
            "last_updated": datetime.utcnow().isoformat()
        }
        with open(self.archive_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def add_generation(self, generation: Generation) -> Generation:
        self.generations[generation.generation_id] = generation
        self.save_archive()
        return generation

    def get_generation(self, gen_id: str) -> Optional[Generation]:
        return self.generations.get(gen_id)

    def get_latest_generation(self) -> Generation:
        sorted_gens = sorted(
            self.generations.values(),
            key=lambda g: int(g.generation_id.split("_")[1]) if "_" in g.generation_id and g.generation_id.split("_")[1].isdigit() else 0
        )
        return sorted_gens[-1] if sorted_gens else self.generations["gen_0"]

    def get_all_generations(self) -> List[Generation]:
        return sorted(
            list(self.generations.values()),
            key=lambda g: int(g.generation_id.split("_")[1]) if "_" in g.generation_id and g.generation_id.split("_")[1].isdigit() else 0
        )

# Global singleton archive manager
archive_manager = ArchiveManager()
