"""Tests for configuration models."""

import pytest
from pydantic import ValidationError

from seafarer.config import (
    BlobStorageConfig,
    PipelineConfig,
    SinkConfig,
    SourceConfig,
)


def test_blob_storage_config():
    """Test BlobStorageConfig creation."""
    config = BlobStorageConfig(
        connection_string="test_connection_string",
        container_name="test_container",
    )
    assert config.connection_string == "test_connection_string"
    assert config.container_name == "test_container"


def test_blob_storage_config_immutable():
    """Test that BlobStorageConfig is immutable."""
    config = BlobStorageConfig(
        connection_string="test_connection_string",
        container_name="test_container",
    )
    with pytest.raises(ValidationError):
        config.connection_string = "new_value"


def test_source_config():
    """Test SourceConfig creation."""
    blob_config = BlobStorageConfig(
        connection_string="test_connection_string",
        container_name="input-data",
    )
    source_config = SourceConfig(blob_storage=blob_config)
    assert source_config.blob_storage.container_name == "input-data"


def test_sink_config():
    """Test SinkConfig creation."""
    blob_config = BlobStorageConfig(
        connection_string="test_connection_string",
        container_name="output-data",
    )
    sink_config = SinkConfig(blob_storage=blob_config)
    assert sink_config.blob_storage.container_name == "output-data"


def test_pipeline_config():
    """Test PipelineConfig creation."""
    source_blob = BlobStorageConfig(
        connection_string="source_conn",
        container_name="input-data",
    )
    sink_blob = BlobStorageConfig(
        connection_string="sink_conn",
        container_name="output-data",
    )
    source = SourceConfig(blob_storage=source_blob)
    sink = SinkConfig(blob_storage=sink_blob)
    
    config = PipelineConfig(source=source, sink=sink)
    assert config.source.blob_storage.container_name == "input-data"
    assert config.sink.blob_storage.container_name == "output-data"
    assert config.batch_size == 1000


def test_pipeline_config_custom_batch_size():
    """Test PipelineConfig with custom batch size."""
    source_blob = BlobStorageConfig(
        connection_string="source_conn",
        container_name="input-data",
    )
    sink_blob = BlobStorageConfig(
        connection_string="sink_conn",
        container_name="output-data",
    )
    source = SourceConfig(blob_storage=source_blob)
    sink = SinkConfig(blob_storage=sink_blob)
    
    config = PipelineConfig(source=source, sink=sink, batch_size=500)
    assert config.batch_size == 500
