"""Tests for configuration models."""

import pytest
from pydantic import ValidationError

from seafarer.config import BlobStorageConfig, SourcePortConfig, SinkPortConfig


def test_blob_storage_config_valid(blob_storage_config_dict: dict) -> None:
    """Test that valid blob storage configuration is accepted."""
    config = BlobStorageConfig(**blob_storage_config_dict)
    
    assert config.account_name == blob_storage_config_dict["account_name"]
    assert config.account_key == blob_storage_config_dict["account_key"]
    assert config.endpoint == blob_storage_config_dict["endpoint"]
    assert config.container_name == blob_storage_config_dict["container_name"]


def test_blob_storage_config_missing_field() -> None:
    """Test that missing required fields raise validation errors."""
    with pytest.raises(ValidationError):
        BlobStorageConfig(
            account_name="test",
            account_key="key",
            endpoint="http://localhost"
            # Missing container_name
        )


def test_blob_storage_config_immutable(blob_storage_config_dict: dict) -> None:
    """Test that configuration is immutable (frozen)."""
    config = BlobStorageConfig(**blob_storage_config_dict)
    
    with pytest.raises(ValidationError):
        config.account_name = "new_name"  # type: ignore


def test_source_port_config_valid(blob_storage_config_dict: dict) -> None:
    """Test that valid source port configuration is accepted."""
    blob_config = BlobStorageConfig(**blob_storage_config_dict)
    config = SourcePortConfig(
        blob_storage=blob_config,
        blob_path="data/input.csv"
    )
    
    assert config.blob_storage == blob_config
    assert config.blob_path == "data/input.csv"


def test_sink_port_config_valid(blob_storage_config_dict: dict) -> None:
    """Test that valid sink port configuration is accepted."""
    blob_config = BlobStorageConfig(**blob_storage_config_dict)
    config = SinkPortConfig(
        blob_storage=blob_config,
        blob_path="data/output.parquet"
    )
    
    assert config.blob_storage == blob_config
    assert config.blob_path == "data/output.parquet"


def test_source_port_config_immutable(blob_storage_config_dict: dict) -> None:
    """Test that source port configuration is immutable."""
    blob_config = BlobStorageConfig(**blob_storage_config_dict)
    config = SourcePortConfig(
        blob_storage=blob_config,
        blob_path="data/input.csv"
    )
    
    with pytest.raises(ValidationError):
        config.blob_path = "new_path.csv"  # type: ignore
