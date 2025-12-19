from fastapi import APIRouter

# Create main router
router = APIRouter()

# Import all routers to ensure they are registered
from app.routes import pdf_routes, podcast_routes, voice_routes, auth_routes, qdrant_routes
