from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import pdf_routes, podcast_routes, voice_routes, auth_routes
from app.config import settings

app = FastAPI(
    title="Podcast Generator API",
    description="API for generating podcasts from PDF documents",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_routes.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(pdf_routes.router, prefix="/api/pdf", tags=["PDF Processing"])
app.include_router(podcast_routes.router, prefix="/api/podcast", tags=["Podcast Generation"])
app.include_router(voice_routes.router, prefix="/api/voice", tags=["Voice Interaction"])

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
