import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.routes import router as v1_router

def create_app() -> FastAPI:
    app = FastAPI(
        title="Research-Grade Interview Generator",
        description="FastAPI backend leveraging HF Inference for semantic question generation.",
        version="1.0.0"
    )

    # Configure CORS for frontend integration
    app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"], # Specific URL required for credentials
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

    # Register API routes
    app.include_router(v1_router, prefix="/api/v1")

    return app

app = create_app()

if __name__ == "__main__":
    # Production-ready entry point
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=False,
        workers=4
    )