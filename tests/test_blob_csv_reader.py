"""Tests for BlobCSVReader source port."""

from io import BytesIO
from unittest.mock import Mock, MagicMock, patch
import pandas as pd
import pytest

from seafarer.config import BlobStorageConfig, SourcePortConfig
from seafarer.ports.blob_csv_reader import BlobCSVReader


@pytest.fixture
def source_config(blob_storage_config_dict: dict) -> SourcePortConfig:
    """Provide a source port configuration."""
    blob_config = BlobStorageConfig(**blob_storage_config_dict)
    return SourcePortConfig(
        blob_storage=blob_config,
        blob_path="data/input.csv"
    )


@pytest.fixture
def mock_blob_service_client() -> Mock:
    """Provide a mock BlobServiceClient."""
    return Mock()


def test_blob_csv_reader_initialization(source_config: SourcePortConfig) -> None:
    """Test that BlobCSVReader initializes correctly."""
    with patch('seafarer.ports.blob_csv_reader.BlobServiceClient') as mock_client_class:
        mock_client_class.from_connection_string.return_value = Mock()
        
        reader = BlobCSVReader(source_config)
        
        assert reader._config == source_config
        assert reader._client is not None
        mock_client_class.from_connection_string.assert_called_once()


def test_blob_csv_reader_connection_string_format(source_config: SourcePortConfig) -> None:
    """Test that connection string is formatted correctly without emulator-specific logic."""
    with patch('seafarer.ports.blob_csv_reader.BlobServiceClient') as mock_client_class:
        mock_client_class.from_connection_string.return_value = Mock()
        
        BlobCSVReader(source_config)
        
        # Get the connection string that was used
        call_args = mock_client_class.from_connection_string.call_args
        connection_string = call_args[0][0]
        
        # Verify it contains the expected components without hardcoded emulator values
        assert f"AccountName={source_config.blob_storage.account_name}" in connection_string
        assert f"AccountKey={source_config.blob_storage.account_key}" in connection_string
        assert f"BlobEndpoint={source_config.blob_storage.endpoint}" in connection_string
        assert "DefaultEndpointsProtocol=http" in connection_string


def test_blob_csv_reader_read(source_config: SourcePortConfig, sample_dataframe: pd.DataFrame) -> None:
    """Test reading CSV data from blob storage."""
    # Create CSV bytes from sample dataframe
    csv_buffer = BytesIO()
    sample_dataframe.to_csv(csv_buffer, index=False)
    csv_bytes = csv_buffer.getvalue()
    
    with patch('seafarer.ports.blob_csv_reader.BlobServiceClient') as mock_client_class:
        # Setup mock chain
        mock_client = Mock()
        mock_container_client = Mock()
        mock_blob_client = Mock()
        mock_blob_data = Mock()
        
        mock_client_class.from_connection_string.return_value = mock_client
        mock_client.get_container_client.return_value = mock_container_client
        mock_container_client.get_blob_client.return_value = mock_blob_client
        mock_blob_client.download_blob.return_value = mock_blob_data
        mock_blob_data.readall.return_value = csv_bytes
        
        reader = BlobCSVReader(source_config)
        result = reader.read()
        
        # Verify the result matches the sample dataframe
        pd.testing.assert_frame_equal(result, sample_dataframe)
        
        # Verify correct methods were called
        mock_client.get_container_client.assert_called_once_with(source_config.blob_storage.container_name)
        mock_container_client.get_blob_client.assert_called_once_with(source_config.blob_path)
        mock_blob_client.download_blob.assert_called_once()


def test_blob_csv_reader_read_uninitialized() -> None:
    """Test that reading without initialization raises an error."""
    with patch('seafarer.ports.blob_csv_reader.BlobServiceClient') as mock_client_class:
        mock_client_class.from_connection_string.return_value = Mock()
        
        source_config = SourcePortConfig(
            blob_storage=BlobStorageConfig(
                account_name="test",
                account_key="key",
                endpoint="http://test",
                container_name="test"
            ),
            blob_path="test.csv"
        )
        
        reader = BlobCSVReader(source_config)
        reader._client = None  # Simulate uninitialized state
        
        with pytest.raises(ValueError, match="Client not initialized"):
            reader.read()


def test_blob_csv_reader_close(source_config: SourcePortConfig) -> None:
    """Test closing the BlobCSVReader."""
    with patch('seafarer.ports.blob_csv_reader.BlobServiceClient') as mock_client_class:
        mock_client = Mock()
        mock_client_class.from_connection_string.return_value = mock_client
        
        reader = BlobCSVReader(source_config)
        reader.close()
        
        mock_client.close.assert_called_once()
        assert reader._client is None


def test_blob_csv_reader_close_idempotent(source_config: SourcePortConfig) -> None:
    """Test that closing multiple times doesn't raise errors."""
    with patch('seafarer.ports.blob_csv_reader.BlobServiceClient') as mock_client_class:
        mock_client = Mock()
        mock_client_class.from_connection_string.return_value = mock_client
        
        reader = BlobCSVReader(source_config)
        reader.close()
        reader.close()  # Should not raise an error
        
        mock_client.close.assert_called_once()
