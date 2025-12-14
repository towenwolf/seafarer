"""Blob storage CSV reader port implementation."""

from typing import Iterator

import pandas as pd
from azure.storage.blob import BlobServiceClient

from seafarer.ports.base import SourcePort


class BlobCsvReader(SourcePort):
    """Read CSV files from Azure Blob Storage.
    
    This port implementation reads CSV data from Azure Blob Storage
    and yields pandas DataFrames for processing.
    """

    def __init__(self, connection_string: str, container_name: str, blob_name: str):
        """Initialize the blob CSV reader.
        
        Args:
            connection_string: Azure Storage connection string.
            container_name: Name of the container.
            blob_name: Name of the blob (CSV file).
        """
        self.connection_string = connection_string
        self.container_name = container_name
        self.blob_name = blob_name
        self._client = None

    def read(self) -> Iterator[pd.DataFrame]:
        """Read CSV data from blob storage.
        
        Returns:
            Iterator yielding pandas DataFrames with CSV data.
        """
        blob_service_client = BlobServiceClient.from_connection_string(
            self.connection_string
        )
        blob_client = blob_service_client.get_blob_client(
            container=self.container_name, blob=self.blob_name
        )

        # Download blob content
        blob_data = blob_client.download_blob()
        content = blob_data.readall()

        # Parse CSV content
        import io

        df = pd.read_csv(io.BytesIO(content))
        yield df

    def close(self) -> None:
        """Close connections and cleanup resources."""
        # BlobServiceClient doesn't require explicit cleanup
        pass
