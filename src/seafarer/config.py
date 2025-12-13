"""Configuration models for seafarer ports."""

from pydantic import BaseModel, ConfigDict, Field


class BlobStorageConfig(BaseModel):
    """Configuration for Azure Blob Storage connection.
    
    This configuration is generic and does not contain any emulator-specific logic.
    It can be used with both Azure Blob Storage and Azurite emulator.
    """

    model_config = ConfigDict(frozen=True)

    account_name: str = Field(..., description="Storage account name")
    account_key: str = Field(..., description="Storage account key")
    endpoint: str = Field(..., description="Blob storage endpoint URL")
    container_name: str = Field(..., description="Container name")


class SourcePortConfig(BaseModel):
    """Configuration for source port (CSV reader)."""

    model_config = ConfigDict(frozen=True)

    blob_storage: BlobStorageConfig = Field(..., description="Blob storage configuration")
    blob_path: str = Field(..., description="Path to the blob within the container")


class SinkPortConfig(BaseModel):
    """Configuration for sink port (Parquet writer)."""

    model_config = ConfigDict(frozen=True)

    blob_storage: BlobStorageConfig = Field(..., description="Blob storage configuration")
    blob_path: str = Field(..., description="Path to the blob within the container")
