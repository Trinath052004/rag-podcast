import pytest
from unittest.mock import patch, MagicMock
from app.services.qdrant_service import QdrantService
from app.models.qdrant_client import VectorSearchResult, QdrantCollectionConfig
from app.models.pdf_processing import PDFChunk
from datetime import datetime

@pytest.fixture
def qdrant_service():
    return QdrantService()

@pytest.fixture
def sample_chunks():
    return [
        PDFChunk(
            id="1",
            content="Sample content for testing",
            page_number=1,
            embedding=[0.1, 0.2, 0.3, 0.4],
            metadata={"source": "test.pdf", "timestamp": datetime.now().isoformat()}
        ),
        PDFChunk(
            id="2",
            content="Another test content",
            page_number=2,
            embedding=[0.5, 0.6, 0.7, 0.8],
            metadata={"source": "test.pdf", "timestamp": datetime.now().isoformat()}
        )
    ]

def test_collection_creation(qdrant_service):
    """Test Qdrant collection creation"""
    config = QdrantCollectionConfig(
        collection_name="test_collection",
        vector_size=384,
        distance_metric="cosine"
    )

    with patch.object(qdrant_service.client, 'create_collection') as mock_create:
        mock_create.return_value = None
        result = qdrant_service.create_collection(config)

        assert result is True
        mock_create.assert_called_once()

def test_collection_exists(qdrant_service):
    """Test collection existence check"""
    with patch.object(qdrant_service.client, 'collection_exists') as mock_exists:
        mock_exists.return_value = True
        result = qdrant_service.collection_exists("test_collection")

        assert result is True
        mock_exists.assert_called_once_with("test_collection")

def test_vector_upsert(qdrant_service, sample_chunks):
    """Test vector upsert functionality"""
    with patch.object(qdrant_service.client, 'upsert') as mock_upsert:
        mock_upsert.return_value = None
        result = qdrant_service.upsert_vectors("test_collection", sample_chunks)

        assert result is True
        mock_upsert.assert_called_once()

        # Check the call arguments
        call_args = mock_upsert.call_args
        assert call_args[1]['collection_name'] == "test_collection"
        assert len(call_args[1]['points']) == len(sample_chunks)

        # Check point structure
        for point in call_args[1]['points']:
            assert hasattr(point, 'id')
            assert hasattr(point, 'vector')
            assert hasattr(point, 'payload')

def test_vector_search(qdrant_service):
    """Test vector similarity search"""
    query_vector = [0.1, 0.2, 0.3, 0.4]
    mock_result = MagicMock()
    mock_result.id = "test-id"
    mock_result.score = 0.95
    mock_result.payload = {"content": "test content", "page_number": 1}
    mock_result.vector = query_vector

    with patch.object(qdrant_service.client, 'search') as mock_search:
        mock_search.return_value = [mock_result]
        results = qdrant_service.search_similar("test_collection", query_vector, limit=5)

        assert len(results) == 1
        assert isinstance(results[0], VectorSearchResult)
        assert results[0].id == "test-id"
        assert results[0].score == 0.95
        assert results[0].payload == {"content": "test content", "page_number": 1}

def test_get_collection_info(qdrant_service):
    """Test collection information retrieval"""
    mock_collection_info = MagicMock()
    mock_collection_info.vectors_count = 100
    mock_collection_info.points_count = 100
    mock_collection_info.config = {"vector_size": 384, "distance": "Cosine"}

    with patch.object(qdrant_service.client, 'get_collection') as mock_get:
        mock_get.return_value = mock_collection_info
        result = qdrant_service.get_collection_info("test_collection")

        assert result['name'] == "test_collection"
        assert result['vectors_count'] == 100
        assert result['points_count'] == 100
        assert 'config' in result

def test_delete_collection(qdrant_service):
    """Test collection deletion"""
    with patch.object(qdrant_service.client, 'delete_collection') as mock_delete:
        mock_delete.return_value = None
        result = qdrant_service.delete_collection("test_collection")

        assert result is True
        mock_delete.assert_called_once_with("test_collection")

def test_initialize_default_collection(qdrant_service):
    """Test default collection initialization"""
    with patch.object(qdrant_service, 'collection_exists') as mock_exists, \
         patch.object(qdrant_service, 'create_collection') as mock_create:

        # Test when collection doesn't exist
        mock_exists.return_value = False
        mock_create.return_value = True

        with patch('sentence_transformers.SentenceTransformer') as mock_transformer:
            mock_model = MagicMock()
            mock_model.encode.return_value = [[0.1, 0.2, 0.3, 0.4]]
            mock_transformer.return_value = mock_model

            collection_name = qdrant_service.initialize_default_collection()

            assert collection_name == "podcast_chunks"
            mock_create.assert_called_once()

        # Test when collection already exists
        mock_exists.return_value = True
        collection_name = qdrant_service.initialize_default_collection()
        assert collection_name == "podcast_chunks"
        mock_create.assert_not_called()

def test_error_handling(qdrant_service):
    """Test error handling in Qdrant operations"""
    # Test collection creation error
    with patch.object(qdrant_service.client, 'create_collection') as mock_create:
        mock_create.side_effect = Exception("Connection error")
        result = qdrant_service.create_collection(QdrantCollectionConfig(
            collection_name="test", vector_size=384
        ))
        assert result is False

    # Test search error
    with patch.object(qdrant_service.client, 'search') as mock_search:
        mock_search.side_effect = Exception("Search error")
        results = qdrant_service.search_similar("test", [0.1, 0.2, 0.3])
        assert len(results) == 0

    # Test collection info error
    with patch.object(qdrant_service.client, 'get_collection') as mock_get:
        mock_get.side_effect = Exception("Collection error")
        result = qdrant_service.get_collection_info("test")
        assert result == {}
