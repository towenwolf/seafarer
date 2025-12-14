"""Blob storage Parquet writer port implementation."""

import io

import pandas as pd
from azure.core.exceptions import ResourceExistsError
from azure.storage.blob import BlobServiceClient

from seafarer.ports.base import SinkPort


class BlobParquetWriter(SinkPort):
    """Write Parquet files to Azure Blob Storage.
    
    This port implementation writes pandas DataFrames as Parquet files
    to Azure Blob Storage.
    """

    def __init__(self, connection_string: str, container_name: str, blob_name: str):
        """Initialize the blob Parquet writer.
        
        Args:
            connection_string: Azure Storage connection string.
            container_name: Name of the container.
            blob_name: Name of the blob (Parquet file).
        """
        self.connection_string = connection_string
        self.container_name = container_name
        self.blob_name = blob_name
        self._client = None

    def write(self, data: pd.DataFrame) -> None:
        """Write DataFrame to blob storage as Parquet.
        
        Args:
            data: pandas DataFrame to write as Parquet.
        """
        blob_service_client = BlobServiceClient.from_connection_string(
            self.connection_string
        )
        
        # Ensure container exists
        container_client = blob_service_client.get_container_client(
            self.container_name
        )
        try:
            container_client.create_container()
        except ResourceExistsError:
            # Container already exists
            pass

        # Convert DataFrame to Parquet bytes
        buffer = io.BytesIO()
        data.to_parquet(buffer, engine="pyarrow", index=False)
        buffer.seek(0)

        # Upload to blob storage
        blob_client = blob_service_client.get_blob_client(
            container=self.container_name, blob=self.blob_name
        )
        blob_client.upload_blob(buffer, overwrite=True)

    def close(self) -> None:
        """Close connections and cleanup resources."""
        # BlobServiceClient doesn't require explicit cleanup
        pass
