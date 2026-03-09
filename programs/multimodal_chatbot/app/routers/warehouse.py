"""
Warehouse status endpoint — stub for future hardware integration.

TO DELETE: remove this file and the two lines in app/main.py that
import and mount this router (search for "warehouse").
"""

import random

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/warehouse", tags=["warehouse"])


class WarehouseStatusResponse(BaseModel):
    """Response returned by the warehouse status endpoint."""

    status: str


@router.get("/open", response_model=WarehouseStatusResponse)
async def warehouse_open() -> WarehouseStatusResponse:
    """
    Return a random warehouse door status.

    Returns "opened" or "closed" with equal probability.
    This is a stub — replace the body with real hardware logic when ready.
    """
    status = random.choice(["opened", "closed"])
    return WarehouseStatusResponse(status=status)
