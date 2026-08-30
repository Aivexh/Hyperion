from app.evaluation.plot_generator import generate_performance_plots
from app.hyperagent.meta_agent import meta_agent_mutator
from app.hyperagent.archive import archive_manager
import os
import sys
import json
import asyncio

# Ensure app package is in path
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")))


async def run_evaluation_pipeline(num_generations: int = 5):
    """
    Runs an automated multi-generation evolution pipeline benchmark,
    verifying self-improvement performance metrics and generating visual plots.
    """
    print("=" * 70)
    print(
        f"STARTING HYPERAGENT SELF-IMPROVEMENT EVALUATION PIPELINE ({num_generations} GENERATIONS)")
    print("=" * 70)

    for step in range(1, num_generations + 1):
        print(f"\n--- EVOLUTION CYCLE {step}/{num_generations} ---")
        async for event in meta_agent_mutator.evolve_next_generation():
            if event.get("type") == "log":
                print(f"[LOG] {event['message']}")
            elif event.get("type") == "generation_created":
                gen = event["generation"]
                print(
                    f"[SUCCESS] Created {gen['generation_id']} | Score: {gen['score']} (+{event['score_delta']} pts)")

    # Load final archive and plot
    archive_file = archive_manager.archive_path
    if os.path.exists(archive_file):
        with open(archive_file, "r", encoding="utf-8") as f:
            archive_data = json.load(f)
        plots_dir = os.path.join(os.path.dirname(__file__), "plots")
        generate_performance_plots(archive_data, plots_dir)

    print("\n" + "=" * 70)
    print("EVALUATION PIPELINE COMPLETED SUCCESSFULLY!")
    print(
        f"Total Generations Archived: {len(archive_manager.get_all_generations())}")
    print(
        f"Baseline G0 Score: {archive_manager.get_all_generations()[0].score}")
    print(
        f"Latest Generation Score: {archive_manager.get_latest_generation().score}")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(run_evaluation_pipeline(num_generations=5))
