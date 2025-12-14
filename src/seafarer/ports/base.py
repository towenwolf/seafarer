"""Base port abstractions for Hexagonal Architecture."""

from abc import ABC, abstractmethod
from typing import Any, Iterator


class SourcePort(ABC):
    """Abstract base class for data source ports.
    
    SourcePort defines the interface for reading data from external sources.
    Implementations handle specific source types (e.g., blob storage, databases).
    """

    @abstractmethod
    def read(self) -> Iterator[Any]:
        """Read data from the source.
        
        Returns:
            Iterator yielding data items from the source.
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the source connection and cleanup resources."""
        pass

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


class SinkPort(ABC):
    """Abstract base class for data sink ports.
    
    SinkPort defines the interface for writing data to external destinations.
    Implementations handle specific sink types (e.g., blob storage, databases).
    """

    @abstractmethod
    def write(self, data: Any) -> None:
        """Write data to the sink.
        
        Args:
            data: Data to write to the sink.
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the sink connection and cleanup resources."""
        pass

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
