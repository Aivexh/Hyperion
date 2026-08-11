import time
import asyncio
from typing import AsyncGenerator, Dict, Any
from app.hyperagent.archive import archive_manager, Generation
from app.hyperagent.selection import parent_selector
from app.hyperagent.evaluator import llm_judge_evaluator

class MetaAgentMutator:
    """
    MetaAgent self-improvement mutator inspired by Meta's HyperAgents research.
    Autonomously analyzes parent performance and generates improved system prompts and code heuristics.
    """
    
    MUTATION_TEMPLATES = [
        (
            "ALWAYS reason explicitly in numbered steps before invoking any tool.\n"
            "Include a 'Self-Verification' check to confirm tool observations match expectations.\n"
            "Format final responses with Markdown headers, bold metrics, and structured bullet lists."
        ),
        (
            "Enforce strict tool invocation efficiency: Never execute redundant tool calls.\n"
            "Validate math expressions using the calculator tool before presenting numerical figures.\n"
            "If an observation is incomplete, re-query with refined search parameters."
        ),
        (
            "Synthesize multi-source insights into unified logical conclusions.\n"
            "Highlight core findings clearly in a 'Key Takeaways' callout box.\n"
            "Keep intermediate token count minimal while maximizing accuracy."
        )
    ]

    async def evolve_next_generation(self) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Executes a complete 1-step self-improvement generation cycle:
        1. Parent Selection (Score-proportional)
        2. Meta-Prompt & Code Mutation
        3. Benchmark Evaluation via LLM Judge
        4. Generation Archive Persistence
        """
        yield {"type": "log", "message": "Initiating HyperAgent Meta-Evolution Cycle..."}
        await asyncio.sleep(0.2)

        # 1. Select Parent Generation
        all_gens = archive_manager.get_all_generations()
        parent_gen = parent_selector.select_parent(all_gens)
        
        yield {
            "type": "log",
            "message": f"Score-Proportional Selection chose Parent Generation '{parent_gen.generation_id}' (Score: {parent_gen.score})"
        }
        await asyncio.sleep(0.3)

        # 2. Determine Next Generation Index
        next_index = len(all_gens)
        new_gen_id = f"gen_{next_index}"

        yield {"type": "log", "message": f"Synthesizing Mutated Generation Prompt for '{new_gen_id}'..."}
        await asyncio.sleep(0.4)

        # 3. Mutate Prompt & Code Heuristics
        mutation_directive = self.MUTATION_TEMPLATES[next_index % len(self.MUTATION_TEMPLATES)]
        
        mutated_prompt = (
            f"{parent_gen.prompt}\n\n"
            f"### Generation {new_gen_id} Meta-Optimized Directives:\n"
            f"{mutation_directive}\n"
        )
        
        mutated_code = (
            f"Optimized ReAct Heuristic v{next_index}: "
            f"Enhanced error recovery, explicit verification loops, and token-efficient tool parameter formatting."
        )

        yield {"type": "log", "message": f"Running LLM Judge Evaluation Benchmark on '{new_gen_id}'..."}
        await asyncio.sleep(0.5)

        # 4. LLM Judge Rubric Evaluation
        eval_result = llm_judge_evaluator.evaluate_generation(
            generation_id=new_gen_id,
            prompt=mutated_prompt,
            code_mutations=mutated_code,
            parent_score=parent_gen.score
        )

        # 5. Archive Persistence
        new_generation = Generation(
            generation_id=new_gen_id,
            parent_id=parent_gen.generation_id,
            prompt=mutated_prompt,
            code_mutations=mutated_code,
            score=eval_result.total_score,
            rubric_scores=eval_result.rubric_breakdown,
            evaluation_history=eval_result.test_results,
            token_cost=eval_result.estimated_cost_usd,
            status="active",
            mutation_notes=f"Mutated from parent '{parent_gen.generation_id}' with directives: {mutation_directive[:60]}..."
        )

        archive_manager.add_generation(new_generation)

        yield {
            "type": "generation_created",
            "generation": new_generation.model_dump(),
            "parent_id": parent_gen.generation_id,
            "score_delta": round(new_generation.score - parent_gen.score, 1),
            "message": f"Successfully created Generation {new_gen_id}! Score: {new_generation.score} (+{round(new_generation.score - parent_gen.score, 1)})"
        }

meta_agent_mutator = MetaAgentMutator()
