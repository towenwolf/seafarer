"""Configuration models for Seafarer."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class BlobStorageConfig(BaseModel):
    """Configuration for Azure Blob Storage connection."""

    model_config = ConfigDict(frozen=True)

    connection_string: str = Field(
        ...,
        description="Azure Storage connection string",
    )
    container_name: str = Field(
        ...,
        description="Container name for blob storage",
    )


class SourceConfig(BaseModel):
    """Configuration for data source."""

    model_config = ConfigDict(frozen=True)

    blob_storage: BlobStorageConfig = Field(
        ...,
        description="Blob storage configuration for source",
    )


class SinkConfig(BaseModel):
    """Configuration for data sink."""

    model_config = ConfigDict(frozen=True)

    blob_storage: BlobStorageConfig = Field(
        ...,
        description="Blob storage configuration for sink",
    )


class PipelineConfig(BaseModel):
    """Configuration for the data pipeline."""

    model_config = ConfigDict(frozen=True)

    source: SourceConfig = Field(
        ...,
        description="Source configuration",
    )
    sink: SinkConfig = Field(
        ...,
        description="Sink configuration",
    )
    batch_size: Optional[int] = Field(
        default=1000,
        description="Batch size for processing",
    )
