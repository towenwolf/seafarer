"""Core pipeline service for data processing."""

from typing import Callable, Optional

from seafarer.ports.base import SinkPort, SourcePort


class Pipeline:
    """Data pipeline orchestrator.
    
    The Pipeline coordinates data flow from source to sink, optionally
    applying transformations.
    """

    def __init__(
        self,
        source: SourcePort,
        sink: SinkPort,
        transform: Optional[Callable] = None,
    ):
        """Initialize the pipeline.
        
        Args:
            source: Source port for reading data.
            sink: Sink port for writing data.
            transform: Optional transformation function to apply to data.
        """
        self.source = source
        self.sink = sink
        self.transform = transform

    def run(self) -> None:
        """Execute the pipeline.
        
        Reads data from source, optionally applies transformations,
        and writes to sink.
        """
        with self.source, self.sink:
            for data in self.source.read():
                if self.transform:
                    data = self.transform(data)
                self.sink.write(data)
