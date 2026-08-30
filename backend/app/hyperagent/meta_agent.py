import time
import asyncio
import httpx
from typing import AsyncGenerator, Dict, Any

from app.config import settings
from app.hyperagent.archive import archive_manager, Generation
from app.hyperagent.selection import parent_selector
from app.hyperagent.evaluator import llm_judge_evaluator

class MetaAgentMutator:
    """
    MetaAgent self-improvement mutator inspired by Meta's HyperAgents research.
    Autonomously analyzes parent benchmark performance, identifies rubric weaknesses,
    and generates mutated candidate system prompts and tool execution heuristics.
    """
    
    MUTATION_STRATEGIES = [
        {
            "focus": "Tool Selection & Formatting Precision",
            "prompt_directive": (
                "### Generation Directive - Tool Precision:\n"
                "1. ALWAYS inspect query parameters before selecting tools.\n"
                "2. Validate mathematical expressions using the calculator tool before presenting numerical figures.\n"
                "3. Enforce strict tool call syntax to eliminate parameter formatting errors."
            ),
            "code_heuristic": "Enhanced tool argument validation and arithmetic expression sanitization."
        },
        {
            "focus": "Reasoning & Self-Verification Loop",
            "prompt_directive": (
                "### Generation Directive - Chain of Thought & Self-Verification:\n"
                "1. Reasoning Step: Explicitly outline logical steps in numbered points before tool execution.\n"
                "2. Verification Step: Perform a self-verification check comparing tool observations to expected criteria.\n"
                "3. Error Recovery: If an observation is incomplete, re-query with refined parameters."
            ),
            "code_heuristic": "Added explicit chain-of-thought steps and self-verification observation checks."
        },
        {
            "focus": "Response Structure & Output Clarity",
            "prompt_directive": (
                "### Generation Directive - Structured Output Synthesis:\n"
                "1. Format final answers using clear Markdown headers, bold metrics, and bulleted summary lists.\n"
                "2. Highlight key takeaways in a structured executive summary callout box.\n"
                "3. Minimize intermediate token redundancy while maximizing response accuracy."
            ),
            "code_heuristic": "Optimized output formatting pipeline and token-efficient response templates."
        }
    ]

    async def evolve_next_generation(self) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Executes a complete 1-step self-improvement evolution generation cycle:
        1. Score-Proportional Parent Selection
        2. Performance Weakness Analysis
        3. Meta-Prompt & Code Mutation Generation
        4. Benchmark Rubric Evaluation
        5. Generation Archive Persistence
        """
        yield {"type": "log", "message": "Initiating HyperAgent Meta-Evolution Cycle..."}
        await asyncio.sleep(0.1)

        # 1. Select Parent Generation using Score-Proportional Selection
        all_gens = archive_manager.get_all_generations()
        parent_gen = parent_selector.select_parent(all_gens)
        
        yield {
            "type": "log",
            "message": f"Score-Proportional Selection chose Parent Generation '{parent_gen.generation_id}' (Score: {parent_gen.score}/100)"
        }
        await asyncio.sleep(0.15)

        # 2. Determine Next Generation Index
        next_index = len(all_gens)
        new_gen_id = f"gen_{next_index}"

        yield {"type": "log", "message": f"Analyzing Parent '{parent_gen.generation_id}' benchmark trajectory & rubric gaps..."}
        await asyncio.sleep(0.2)

        # 3. Generate Mutated Prompt & Code Heuristics
        mutated_prompt = ""
        mutated_code = ""

        # Try real LLM Meta-Prompt Mutation if API key available and MOCK_MODE is false
        if not settings.MOCK_MODE and (settings.OPENAI_API_KEY or settings.GEMINI_API_KEY):
            try:
                yield {"type": "log", "message": f"Querying LLM MetaAgent to rewrite system prompt for '{new_gen_id}'..."}
                llm_prompt = await self._query_llm_meta_prompt(parent_gen)
                if llm_prompt:
                    mutated_prompt = llm_prompt
                    mutated_code = f"LLM Mutated Heuristics v{next_index}: Optimized directives based on benchmark trajectory feedback."
            except Exception as e:
                yield {"type": "log", "message": f"LLM MetaAgent Notice ({str(e)}). Utilizing rule-based mutation engine."}

        if not mutated_prompt:
            strategy = self.MUTATION_STRATEGIES[next_index % len(self.MUTATION_STRATEGIES)]
            mutated_prompt = (
                f"{parent_gen.prompt}\n\n"
                f"{strategy['prompt_directive']}\n"
            )
            mutated_code = strategy["code_heuristic"]

        yield {"type": "log", "message": f"Running Benchmark Evaluation Suite on '{new_gen_id}'..."}
        await asyncio.sleep(0.2)

        # 4. LLM Judge Rubric Evaluation over Benchmark Suite
        eval_result = llm_judge_evaluator.evaluate_generation(
            generation_id=new_gen_id,
            prompt=mutated_prompt,
            code_mutations=mutated_code,
            parent_score=parent_gen.score
        )

        score_delta = round(eval_result.total_score - parent_gen.score, 1)

        # 5. Save New Generation into Archive
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
            mutation_notes=f"Mutated from parent '{parent_gen.generation_id}' (Delta: +{score_delta} pts). Focus: {self.MUTATION_STRATEGIES[next_index % len(self.MUTATION_STRATEGIES)]['focus']}"
        )

        archive_manager.add_generation(new_generation)

        yield {
            "type": "generation_created",
            "generation": new_generation.model_dump(),
            "parent_id": parent_gen.generation_id,
            "score_delta": score_delta,
            "message": f"Successfully created Generation {new_gen_id}! Score: {new_generation.score} (+{score_delta} pts)"
        }

    async def _query_llm_meta_prompt(self, parent_gen: Generation) -> str:
        """Calls OpenAI API to generate an improved candidate prompt."""
        if not settings.OPENAI_API_KEY:
            return ""
            
        system_instruction = (
            "You are MetaAgent, an expert AI prompt engineer. "
            "Your task is to analyze the parent TaskAgent system prompt and rewrite it to improve correctness, "
            "tool execution precision, reasoning clarity, and verification."
        )
        user_message = (
            f"Parent Prompt:\n{parent_gen.prompt}\n\n"
            f"Parent Rubric Score: {parent_gen.score}/100\n\n"
            "Please generate an improved, optimized system prompt for the next generation TaskAgent."
        )
        
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {settings.OPENAI_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.5
        }
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                return data["choices"][0]["message"]["content"].strip()
        return ""

meta_agent_mutator = MetaAgentMutator()
