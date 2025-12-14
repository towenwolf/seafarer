"""Command-line interface for Seafarer."""

import click

from seafarer import __version__


@click.group()
@click.version_option(version=__version__)
def cli():
    """Seafarer - A data pipeline infrastructure for CSV-to-Parquet processing."""
    pass


@cli.command()
@click.option(
    "--source-connection",
    required=True,
    help="Azure Storage connection string for source",
)
@click.option(
    "--source-container",
    required=True,
    help="Container name for source",
)
@click.option(
    "--source-blob",
    required=True,
    help="Blob name for source CSV file",
)
@click.option(
    "--sink-connection",
    required=True,
    help="Azure Storage connection string for sink",
)
@click.option(
    "--sink-container",
    required=True,
    help="Container name for sink",
)
@click.option(
    "--sink-blob",
    required=True,
    help="Blob name for sink Parquet file",
)
def run(
    source_connection: str,
    source_container: str,
    source_blob: str,
    sink_connection: str,
    sink_container: str,
    sink_blob: str,
):
    """Run the data pipeline from CSV to Parquet."""
    from seafarer.core.pipeline import Pipeline
    from seafarer.ports.blob_csv_reader import BlobCsvReader
    from seafarer.ports.blob_parquet_writer import BlobParquetWriter

    click.echo("Starting Seafarer pipeline...")

    # Create source and sink ports
    source = BlobCsvReader(source_connection, source_container, source_blob)
    sink = BlobParquetWriter(sink_connection, sink_container, sink_blob)

    # Create and run pipeline
    pipeline = Pipeline(source=source, sink=sink)
    
    try:
        pipeline.run()
        click.echo("Pipeline completed successfully!")
    except Exception as e:
        click.echo(f"Pipeline failed: {e}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    cli()
