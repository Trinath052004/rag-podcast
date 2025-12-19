from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional
from app.services.qdrant_service import QdrantService
from app.models.qdrant_client import QdrantCollectionConfig, VectorSearchResult
from app.config import settings

router = APIRouter()
qdrant_service = QdrantService()

@router.post("/collections", status_code=status.HTTP_201_CREATED)
async def create_collection(config: QdrantCollectionConfig):
    """Create a new Qdrant collection"""
    try:
        success = qdrant_service.create_collection(config)
        if success:
            return {"status": "success", "collection_name": config.collection_name}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create collection"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating collection: {str(e)}"
        )

@router.get("/collections/{collection_name}")
async def get_collection_info(collection_name: str):
    """Get information about a Qdrant collection"""
    try:
        info = qdrant_service.get_collection_info(collection_name)
        if info:
            return info
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Collection not found"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting collection info: {str(e)}"
        )

@router.post("/collections/{collection_name}/search")
async def search_vectors(
    collection_name: str,
    query_vector: list[float] = Query(...),
    limit: int = 5,
    filter: Optional[dict] = None
):
    """Search for similar vectors in a collection"""
    try:
        results = qdrant_service.search_similar(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=limit,
            filter=filter
        )
        return {"results": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching vectors: {str(e)}"
        )

@router.delete("/collections/{collection_name}")
async def delete_collection(collection_name: str):
    """Delete a Qdrant collection"""
    try:
        success = qdrant_service.delete_collection(collection_name)
        if success:
            return {"status": "success", "message": f"Collection {collection_name} deleted"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Collection not found"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting collection: {str(e)}"
        )

@router.post("/initialize")
async def initialize_default_collection():
    """Initialize the default Qdrant collection"""
    try:
        collection_name = qdrant_service.initialize_default_collection()
        return {
            "status": "success",
            "collection_name": collection_name,
            "message": "Default collection initialized"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error initializing default collection: {str(e)}"
        )
