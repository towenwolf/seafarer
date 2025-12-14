"""Tests for port implementations."""

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from seafarer.ports.base import SinkPort, SourcePort
from seafarer.ports.blob_csv_reader import BlobCsvReader
from seafarer.ports.blob_parquet_writer import BlobParquetWriter


def test_source_port_abstract():
    """Test that SourcePort cannot be instantiated."""
    with pytest.raises(TypeError):
        SourcePort()


def test_sink_port_abstract():
    """Test that SinkPort cannot be instantiated."""
    with pytest.raises(TypeError):
        SinkPort()


def test_source_port_context_manager():
    """Test SourcePort context manager."""
    
    class TestSource(SourcePort):
        def read(self):
            yield "data"
        
        def close(self):
            self.closed = True
    
    source = TestSource()
    with source:
        pass
    assert source.closed


def test_sink_port_context_manager():
    """Test SinkPort context manager."""
    
    class TestSink(SinkPort):
        def write(self, data):
            pass
        
        def close(self):
            self.closed = True
    
    sink = TestSink()
    with sink:
        pass
    assert sink.closed


@patch("seafarer.ports.blob_csv_reader.BlobServiceClient")
def test_blob_csv_reader_read(mock_blob_service_client):
    """Test BlobCsvReader reads CSV data."""
    # Setup mock
    mock_client = MagicMock()
    mock_blob_client = MagicMock()
    mock_download = MagicMock()
    
    csv_content = b"name,age\nAlice,30\nBob,25"
    mock_download.readall.return_value = csv_content
    mock_blob_client.download_blob.return_value = mock_download
    mock_client.get_blob_client.return_value = mock_blob_client
    mock_blob_service_client.from_connection_string.return_value = mock_client
    
    # Test
    reader = BlobCsvReader("conn_str", "container", "blob.csv")
    data_frames = list(reader.read())
    
    assert len(data_frames) == 1
    df = data_frames[0]
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["name", "age"]
    assert len(df) == 2


@patch("seafarer.ports.blob_parquet_writer.BlobServiceClient")
def test_blob_parquet_writer_write(mock_blob_service_client):
    """Test BlobParquetWriter writes Parquet data."""
    # Setup mock
    mock_client = MagicMock()
    mock_container_client = MagicMock()
    mock_blob_client = MagicMock()
    
    mock_client.get_container_client.return_value = mock_container_client
    mock_client.get_blob_client.return_value = mock_blob_client
    mock_blob_service_client.from_connection_string.return_value = mock_client
    
    # Test
    writer = BlobParquetWriter("conn_str", "container", "output.parquet")
    df = pd.DataFrame({"name": ["Alice", "Bob"], "age": [30, 25]})
    writer.write(df)
    
    # Verify upload was called
    mock_blob_client.upload_blob.assert_called_once()
