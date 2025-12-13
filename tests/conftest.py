"""Pytest configuration and fixtures."""

import pytest
import pandas as pd


@pytest.fixture
def sample_dataframe() -> pd.DataFrame:
    """Provide a sample DataFrame for testing."""
    return pd.DataFrame({
        "id": [1, 2, 3],
        "name": ["Alice", "Bob", "Charlie"],
        "value": [10.5, 20.3, 30.1]
    })


@pytest.fixture
def blob_storage_config_dict() -> dict:
    """Provide sample blob storage configuration as dict."""
    return {
        "account_name": "devstoreaccount1",
        "account_key": "Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==",
        "endpoint": "http://127.0.0.1:10000/devstoreaccount1",
        "container_name": "test-container"
    }
