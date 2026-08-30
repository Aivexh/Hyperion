import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api import chat, evolve, evolution

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Production-Ready Self-Improving HyperAgent Backend inspired by Meta's HyperAgents research.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Parse CORS Origins from settings
origins = [origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",") if origin.strip()]
if not origins:
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(chat.router, prefix=settings.API_V1_STR)
app.include_router(evolve.router, prefix=settings.API_V1_STR)
app.include_router(evolution.router, prefix=settings.API_V1_STR)

@app.get("/health")
async def health_check():
    """Lightweight health check endpoint for container orchestrators and VPS probes."""
    return {
        "status": "ok",
        "healthy": True,
        "service": settings.PROJECT_NAME,
        "mock_mode": settings.MOCK_MODE
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", settings.PORT))
    uvicorn.run("app.main:app", host=settings.HOST, port=port, reload=False)
