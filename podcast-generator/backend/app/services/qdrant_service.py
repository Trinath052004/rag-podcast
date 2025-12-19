from qdrant_client import QdrantClient, models
from qdrant_client.http.models import PointStruct
from typing import List, Dict, Any, Optional
from app.models.qdrant_client import VectorSearchResult, QdrantCollectionConfig
from app.models.pdf_processing import PDFChunk
from app.config import settings
import uuid
import logging

class QdrantService:
    def __init__(self):
        self.client = QdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT
        )
        self.logger = logging.getLogger(__name__)

    def create_collection(self, config: QdrantCollectionConfig) -> bool:
        """Create a new collection in Qdrant"""
        try:
            self.client.create_collection(
                collection_name=config.collection_name,
                vectors_config=models.VectorParams(
                    size=config.vector_size,
                    distance=models.Distance(config.distance_metric.upper())
                )
            )
            return True
        except Exception as e:
            self.logger.error(f"Error creating collection: {str(e)}")
            return False

    def collection_exists(self, collection_name: str) -> bool:
        """Check if a collection exists"""
        try:
            return self.client.collection_exists(collection_name)
        except Exception:
            return False

    def upsert_vectors(self, collection_name: str, chunks: List[PDFChunk]) -> bool:
        """Upsert vectors into Qdrant collection"""
        try:
            points = []
            for chunk in chunks:
                point = PointStruct(
                    id=str(uuid.uuid4()),
                    vector=chunk.embedding,
                    payload={
                        "pdf_id": chunk.metadata.get("pdf_id", ""),
                        "content": chunk.content,
                        "page_number": chunk.page_number,
                        "source": chunk.metadata.get("source", ""),
                        "chunk_index": chunk.metadata.get("chunk_index", 0)
                    }
                )
                points.append(point)

            self.client.upsert(
                collection_name=collection_name,
                points=points
            )
            return True
        except Exception as e:
            self.logger.error(f"Error upserting vectors: {str(e)}")
            return False

    def search_similar(self, collection_name: str, query_vector: List[float],
                      limit: int = 5, filter: Optional[Dict] = None) -> List[VectorSearchResult]:
        """Search for similar vectors in Qdrant"""
        try:
            search_result = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit,
                query_filter=models.Filter(**filter) if filter else None
            )

            results = []
            for result in search_result:
                vector_result = VectorSearchResult(
                    id=result.id,
                    score=result.score,
                    payload=result.payload,
                    vector=result.vector.tolist() if result.vector else None
                )
                results.append(vector_result)

            return results
        except Exception as e:
            self.logger.error(f"Error searching vectors: {str(e)}")
            return []

    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Get information about a collection"""
        try:
            collection_info = self.client.get_collection(collection_name)
            return {
                "name": collection_name,
                "vectors_count": collection_info.vectors_count,
                "points_count": collection_info.points_count,
                "config": collection_info.config.dict()
            }
        except Exception as e:
            self.logger.error(f"Error getting collection info: {str(e)}")
            return {}

    def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection"""
        try:
            self.client.delete_collection(collection_name)
            return True
        except Exception as e:
            self.logger.error(f"Error deleting collection: {str(e)}")
            return False

    def initialize_default_collection(self) -> str:
        """Initialize the default collection if it doesn't exist"""
        collection_name = settings.QDRANT_COLLECTION

        if not self.collection_exists(collection_name):
            # Create a sample embedding to get vector size
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer('all-MiniLM-L6-v2')
            sample_embedding = model.encode(["sample text"])
            vector_size = len(sample_embedding[0])

            config = QdrantCollectionConfig(
                collection_name=collection_name,
                vector_size=vector_size,
                distance_metric="cosine"
            )

            if self.create_collection(config):
                self.logger.info(f"Created default collection: {collection_name}")
            else:
                self.logger.error(f"Failed to create default collection: {collection_name}")

        return collection_name
