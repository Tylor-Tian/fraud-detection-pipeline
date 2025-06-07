import json
from typing import Optional, List

import click
import uvicorn

from .config import Settings
from .core import FraudDetectionSystem
from .api import app, detector as api_detector, storage as api_storage
from .models import Transaction


@click.group()
@click.option("--config", "config_path", type=click.Path(exists=True), help="Path to configuration YAML file")
@click.pass_context
def cli(ctx: click.Context, config_path: Optional[str] = None) -> None:
    """Fraud detection command line interface."""
    settings = Settings.from_yaml(config_path) if config_path else Settings()
    ctx.obj = {"settings": settings}


@cli.command()
@click.option("--host", default="0.0.0.0", show_default=True, help="Host to bind")
@click.option("--port", default=8000, show_default=True, help="Port to bind")
@click.pass_context
def serve(ctx: click.Context, host: str, port: int) -> None:
    """Start the fraud detection API server."""
    settings: Settings = ctx.obj["settings"]
    detector = FraudDetectionSystem(
        redis_host=settings.redis.host,
        redis_port=settings.redis.port,
        model_path=settings.model.model_path,
    )
    # Expose objects for API module
    global api_detector, api_storage
    api_detector = detector
    api_storage = detector.storage
    uvicorn.run(app, host=host, port=port)


def _load_transactions(file_obj) -> List[Transaction]:
    try:
        data = json.load(file_obj)
        if isinstance(data, dict) and "transactions" in data:
            data = data["transactions"]
    except json.JSONDecodeError:
        file_obj.seek(0)
        data = [json.loads(line) for line in file_obj if line.strip()]
    return [Transaction(**tx) for tx in data]


@cli.command(name="batch")
@click.argument("input_file", type=click.File("r"))
@click.option("--output", "output_file", type=click.File("w"), help="Optional output file")
@click.pass_context
def batch_process(ctx: click.Context, input_file, output_file) -> None:
    """Process a batch of transactions from a JSON file."""
    settings: Settings = ctx.obj["settings"]
    detector = FraudDetectionSystem(
        redis_host=settings.redis.host,
        redis_port=settings.redis.port,
        model_path=settings.model.model_path,
    )
    transactions = _load_transactions(input_file)
    results = [detector.process_transaction(tx) for tx in transactions]
    output_data = [r.dict() for r in results]
    json_output = json.dumps(output_data, indent=2, default=str)
    if output_file:
        output_file.write(json_output)
    else:
        click.echo(json_output)


def main() -> None:
    """Entry point for the ``fraud-detector`` command."""
    cli()


__all__ = ["main"]
