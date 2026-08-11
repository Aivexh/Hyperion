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

# CORS Middleware Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(chat.router, prefix=settings.API_V1_STR)
app.include_router(evolve.router, prefix=settings.API_V1_STR)
app.include_router(evolution.router, prefix=settings.API_V1_STR)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "mock_mode": settings.MOCK_MODE
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
