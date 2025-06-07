from typing import Any, Dict, List
from time import time

from fastapi import Depends, FastAPI, Header, HTTPException, Response, status
from pydantic import BaseModel
from prometheus_client import (
    Counter,
    Histogram,
    CONTENT_TYPE_LATEST,
    generate_latest,
)

from . import __version__
from .models import RiskScore, Transaction

# Global objects that can be patched in tests
# They are initialized to None to avoid heavy dependencies like Redis during import
# Actual application code can replace them with real implementations

detector = None  # type: Any
storage = None  # type: Any

app = FastAPI(title="Fraud Detection API")

# Prometheus metrics
transactions_total = Counter(
    "fraud_detection_transactions_total",
    "Total number of transactions processed",
)
processing_time_seconds = Histogram(
    "fraud_detection_processing_time_seconds",
    "Transaction processing time in seconds",
)


def require_auth(authorization: str = Header(None)) -> str:
    """Simple auth dependency ensuring Authorization header is present."""
    if authorization is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return authorization


@app.get("/health")
def health_check() -> Dict[str, Any]:
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "version": __version__,
        "services": {},
    }


@app.post("/transactions", response_model=RiskScore)
def process_transaction_endpoint(
    transaction: Transaction, authorization: str = Depends(require_auth)
) -> RiskScore:
    """Process a single transaction."""
    start = time()
    result: RiskScore = detector.process_transaction(transaction)  # type: ignore
    transactions_total.inc()
    processing_time_seconds.observe(time() - start)
    return result


class BatchRequest(BaseModel):
    transactions: List[Transaction]


@app.post("/transactions/batch")
def process_batch_endpoint(
    batch: BatchRequest, authorization: str = Depends(require_auth)
) -> Dict[str, Any]:
    """Process a batch of transactions."""
    start = time()
    results = [detector.process_transaction(tx) for tx in batch.transactions]  # type: ignore
    transactions_total.inc(len(results))
    processing_time_seconds.observe(time() - start)
    return {
        "results": [r.dict() for r in results],
        "summary": {"total_processed": len(results)},
    }


@app.get("/users/{user_id}/profile")
def get_user_profile(user_id: str, authorization: str = Depends(require_auth)) -> Dict[str, Any]:
    """Retrieve a user's risk profile."""
    profile = storage.get_user_profile(user_id)  # type: ignore
    if profile is None:
        raise HTTPException(status_code=404, detail="User not found")
    return profile.dict()


@app.get("/metrics")
def metrics() -> Response:
    """Expose Prometheus metrics."""
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)


# Expose app for `uvicorn` entry point
__all__ = ["app"]
