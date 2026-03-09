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

    warehouse_name: str
    status: str


@router.get("/open", response_model=WarehouseStatusResponse)
async def warehouse_open(warehouse_name: str) -> WarehouseStatusResponse:
    """
    Return a random warehouse door status for the given warehouse.

    Args:
        warehouse_name: Name of the warehouse to check.

    Returns "opened" or "closed" with equal probability.
    This is a stub — replace the body with real hardware logic when ready.
    """
    status = random.choice(["opened", "not opened (error)"])
    return WarehouseStatusResponse(warehouse_name=warehouse_name, status=status)
