"""
backend/routers/scoreboard.py
Exposes the GPU-Irrelevance Scoreboard metrics API.
"""

from fastapi import APIRouter
from backend.metrics.irrelevance_score import GPUIrrelevanceCalculator

router = APIRouter(prefix="/api/v1/scoreboard", tags=["Scoreboard"])
calculator = GPUIrrelevanceCalculator()


@router.get("", summary="Fetch the live 10-dimension LEO vs NVIDIA scoreboard")
async def get_scoreboard():
    return calculator.get_10_dimension_scoreboard()
