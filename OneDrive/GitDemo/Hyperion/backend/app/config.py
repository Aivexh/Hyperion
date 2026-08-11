import os
from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent
STORAGE_DIR = BASE_DIR / "app" / "storage"
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
ARCHIVE_FILE = STORAGE_DIR / "archive.json"
PLOTS_DIR = BASE_DIR / "evaluation" / "plots"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

class Settings(BaseSettings):
    PROJECT_NAME: str = "HyperAgent Self-Improving System"
    API_V1_STR: str = ""
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # LLM & Evaluation Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    MOCK_MODE: bool = os.getenv("MOCK_MODE", "true").lower() in ("true", "1", "yes")
    
    # Evolution Parameters (Meta-HyperAgent Research)
    SELECTION_TEMPERATURE: float = 0.7
    MUTATION_RATE: float = 0.5
    MAX_GENERATIONS: int = 20
    
    # Storage Paths
    ARCHIVE_PATH: str = str(ARCHIVE_FILE)
    PLOTS_PATH: str = str(PLOTS_DIR)

    class Config:
        case_sensitive = True

settings = Settings()
