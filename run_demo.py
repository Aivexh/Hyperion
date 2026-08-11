import os
import sys
import subprocess
import argparse

def main():
    parser = argparse.ArgumentParser(description="HyperAgent Self-Improving System Launcher")
    parser.add_argument("--eval", action="store_true", help="Run 5-generation evaluation pipeline")
    parser.add_argument("--backend", action="store_true", help="Launch FastAPI Backend server")
    parser.add_argument("--frontend", action="store_true", help="Launch Streamlit Web UI")
    args = parser.parse_args()

    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.join(project_root, "backend"))

    if args.eval:
        print("🚀 Running Standalone Evaluation Benchmark Loop...")
        from evaluation.run_eval import run_evaluation_pipeline
        import asyncio
        asyncio.run(run_evaluation_pipeline(num_generations=5))
    elif args.backend:
        print("⚡ Starting FastAPI Backend on http://localhost:8000 ...")
        cmd = [sys.executable, "-m", "uvicorn", "app.main:app", "--app-dir", os.path.join(project_root, "backend"), "--host", "0.0.0.0", "--port", "8000", "--reload"]
        subprocess.run(cmd)
    elif args.frontend:
        print("🌐 Starting Streamlit UI on http://localhost:8501 ...")
        cmd = [sys.executable, "-m", "streamlit", "run", os.path.join(project_root, "frontend", "app.py")]
        subprocess.run(cmd)
    else:
        print("Please specify an action: --eval, --backend, or --frontend (or run `docker-compose up --build`).")

if __name__ == "__main__":
    main()
