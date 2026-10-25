"""Consistent response formatting helpers and models."""
from typing import Any, Generic, Optional, TypeVar
from pydantic import BaseModel
from datetime import datetime, timezone

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Standard envelope for VidyaSetu API responses."""
    success: bool = True
    data: Optional[T] = None
    error: Optional[dict] = None
    timestamp: str = datetime.now(timezone.utc).isoformat()
    demo_mode: bool = True
    disclaimer: str = "DEMO DATA ONLY - External integrations are simulated."


def success_response(data: Any, message: str = "") -> dict:
    """Helper for successful responses."""
    return {
        "success": True,
        "data": data,
        "message": message,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "demo_mode": True,
        "disclaimer": "DEMO DATA ONLY - External integrations are simulated.",
    }
