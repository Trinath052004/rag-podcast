from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class VectorSearchResult(BaseModel):
    id: str
    score: float
    payload: Dict[str, Any]
    vector: Optional[List[float]] = None

class QdrantCollectionConfig(BaseModel):
    collection_name: str
    vector_size: int
    distance_metric: str = "cosine"

class QdrantUpsertRequest(BaseModel):
    collection_name: str
    points: List[Dict[str, Any]]

class QdrantSearchRequest(BaseModel):
    collection_name: str
    query_vector: List[float]
    limit: int = 5
    filter: Optional[Dict[str, Any]] = None

class QdrantCollectionInfo(BaseModel):
    name: str
    vectors_count: int
    points_count: int
    config: Dict[str, Any]
