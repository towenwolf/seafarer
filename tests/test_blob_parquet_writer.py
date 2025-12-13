"""Tests for BlobParquetWriter sink port."""

from io import BytesIO
from unittest.mock import Mock, MagicMock, patch, call
import pandas as pd
import pytest

from seafarer.config import BlobStorageConfig, SinkPortConfig
from seafarer.ports.blob_parquet_writer import BlobParquetWriter


@pytest.fixture
def sink_config(blob_storage_config_dict: dict) -> SinkPortConfig:
    """Provide a sink port configuration."""
    blob_config = BlobStorageConfig(**blob_storage_config_dict)
    return SinkPortConfig(
        blob_storage=blob_config,
        blob_path="data/output.parquet"
    )


@pytest.fixture
def mock_blob_service_client() -> Mock:
    """Provide a mock BlobServiceClient."""
    return Mock()


def test_blob_parquet_writer_initialization(sink_config: SinkPortConfig) -> None:
    """Test that BlobParquetWriter initializes correctly."""
    with patch('seafarer.ports.blob_parquet_writer.BlobServiceClient') as mock_client_class:
        mock_client_class.from_connection_string.return_value = Mock()
        
        writer = BlobParquetWriter(sink_config)
        
        assert writer._config == sink_config
        assert writer._client is not None
        mock_client_class.from_connection_string.assert_called_once()


def test_blob_parquet_writer_connection_string_format(sink_config: SinkPortConfig) -> None:
    """Test that connection string is formatted correctly without emulator-specific logic."""
    with patch('seafarer.ports.blob_parquet_writer.BlobServiceClient') as mock_client_class:
        mock_client_class.from_connection_string.return_value = Mock()
        
        BlobParquetWriter(sink_config)
        
        # Get the connection string that was used
        call_args = mock_client_class.from_connection_string.call_args
        connection_string = call_args[0][0]
        
        # Verify it contains the expected components without hardcoded emulator values
        assert f"AccountName={sink_config.blob_storage.account_name}" in connection_string
        assert f"AccountKey={sink_config.blob_storage.account_key}" in connection_string
        assert f"BlobEndpoint={sink_config.blob_storage.endpoint}" in connection_string
        assert "DefaultEndpointsProtocol=http" in connection_string


def test_blob_parquet_writer_write(sink_config: SinkPortConfig, sample_dataframe: pd.DataFrame) -> None:
    """Test writing Parquet data to blob storage."""
    with patch('seafarer.ports.blob_parquet_writer.BlobServiceClient') as mock_client_class:
        # Setup mock chain
        mock_client = Mock()
        mock_container_client = Mock()
        mock_blob_client = Mock()
        
        mock_client_class.from_connection_string.return_value = mock_client
        mock_client.get_container_client.return_value = mock_container_client
        mock_container_client.get_blob_client.return_value = mock_blob_client
        
        writer = BlobParquetWriter(sink_config)
        writer.write(sample_dataframe)
        
        # Verify correct methods were called
        mock_client.get_container_client.assert_called_once_with(sink_config.blob_storage.container_name)
        mock_container_client.get_blob_client.assert_called_once_with(sink_config.blob_path)
        mock_blob_client.upload_blob.assert_called_once()
        
        # Verify that upload_blob was called with overwrite=True
        call_args = mock_blob_client.upload_blob.call_args
        assert call_args[1]['overwrite'] is True
        
        # Verify the uploaded data is valid parquet
        uploaded_bytes = call_args[0][0]
        result_df = pd.read_parquet(BytesIO(uploaded_bytes))
        pd.testing.assert_frame_equal(result_df, sample_dataframe)


def test_blob_parquet_writer_write_uninitialized() -> None:
    """Test that writing without initialization raises an error."""
    with patch('seafarer.ports.blob_parquet_writer.BlobServiceClient') as mock_client_class:
        mock_client_class.from_connection_string.return_value = Mock()
        
        sink_config = SinkPortConfig(
            blob_storage=BlobStorageConfig(
                account_name="test",
                account_key="key",
                endpoint="http://test",
                container_name="test"
            ),
            blob_path="test.parquet"
        )
        
        writer = BlobParquetWriter(sink_config)
        writer._client = None  # Simulate uninitialized state
        
        with pytest.raises(ValueError, match="Client not initialized"):
            writer.write(pd.DataFrame({"a": [1, 2, 3]}))


def test_blob_parquet_writer_close(sink_config: SinkPortConfig) -> None:
    """Test closing the BlobParquetWriter."""
    with patch('seafarer.ports.blob_parquet_writer.BlobServiceClient') as mock_client_class:
        mock_client = Mock()
        mock_client_class.from_connection_string.return_value = mock_client
        
        writer = BlobParquetWriter(sink_config)
        writer.close()
        
        mock_client.close.assert_called_once()
        assert writer._client is None


def test_blob_parquet_writer_close_idempotent(sink_config: SinkPortConfig) -> None:
    """Test that closing multiple times doesn't raise errors."""
    with patch('seafarer.ports.blob_parquet_writer.BlobServiceClient') as mock_client_class:
        mock_client = Mock()
        mock_client_class.from_connection_string.return_value = mock_client
        
        writer = BlobParquetWriter(sink_config)
        writer.close()
        writer.close()  # Should not raise an error
        
        mock_client.close.assert_called_once()


def test_blob_parquet_writer_preserves_data_types(sink_config: SinkPortConfig) -> None:
    """Test that data types are preserved when writing to parquet."""
    # Create a dataframe with various data types
    test_df = pd.DataFrame({
        "int_col": [1, 2, 3],
        "float_col": [1.1, 2.2, 3.3],
        "str_col": ["a", "b", "c"],
        "bool_col": [True, False, True]
    })
    
    with patch('seafarer.ports.blob_parquet_writer.BlobServiceClient') as mock_client_class:
        mock_client = Mock()
        mock_container_client = Mock()
        mock_blob_client = Mock()
        
        mock_client_class.from_connection_string.return_value = mock_client
        mock_client.get_container_client.return_value = mock_container_client
        mock_container_client.get_blob_client.return_value = mock_blob_client
        
        writer = BlobParquetWriter(sink_config)
        writer.write(test_df)
        
        # Get the uploaded bytes
        call_args = mock_blob_client.upload_blob.call_args
        uploaded_bytes = call_args[0][0]
        
        # Read back and verify data types are preserved
        result_df = pd.read_parquet(BytesIO(uploaded_bytes))
        pd.testing.assert_frame_equal(result_df, test_df)
        assert result_df.dtypes.to_dict() == test_df.dtypes.to_dict()
