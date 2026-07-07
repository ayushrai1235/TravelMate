from __future__ import annotations

import logging
from typing import Any

from langchain.tools import tool
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class CalculateBudgetInput(BaseModel):
    legs: list[dict[str, Any]] = Field(..., description="List of transport legs with costs")
    group_adults: int = Field(default=1, description="Number of adults")
    group_children: int = Field(default=0, description="Number of children")
    group_seniors: int = Field(default=0, description="Number of seniors")
    days: int = Field(default=1, description="Number of travel days")
    budget_tier: str = Field(default="mid", description="Budget tier: budget, mid, premium")


@tool("calculate_budget", args_schema=CalculateBudgetInput)
async def calculate_budget(
    legs: list[dict[str, Any]],
    group_adults: int = 1,
    group_children: int = 0,
    group_seniors: int = 0,
    days: int = 1,
    budget_tier: str = "mid",
) -> dict[str, Any]:
    """Calculate total trip budget from transport legs and group configuration."""
    try:
        transport_total_min = sum(
            leg.get("cost_inr", {}).get("min", 0) for leg in legs if leg.get("cost_inr")
        )
        transport_total_max = sum(
            leg.get("cost_inr", {}).get("max", 0) for leg in legs if leg.get("cost_inr")
        )

        food_per_person = {"budget": (100, 250), "mid": (200, 400), "premium": (400, 800)}.get(budget_tier, (200, 400))
        accommodation_per_night = {"budget": (500, 1200), "mid": (1500, 3500), "premium": (4000, 8000)}.get(budget_tier, (1500, 3500))

        total_people = group_adults + group_children + group_seniors
        food_total_min = food_per_person[0] * total_people * days
        food_total_max = food_per_person[1] * total_people * days

        result = {
            "budget": {
                "transport": {
                    "legs": [
                        {
                            "leg_id": f"leg_{i+1:03d}",
                            "mode": leg.get("mode", "UNKNOWN"),
                            "cost_inr": leg.get("cost_inr", {"min": 0, "max": 0}),
                        }
                        for i, leg in enumerate(legs)
                    ],
                    "total": {"min": transport_total_min, "max": transport_total_max},
                },
                "food_estimate": {
                    "per_person_per_day": {"min": food_per_person[0], "max": food_per_person[1]},
                    "total": {"min": food_total_min, "max": food_total_max},
                    "basis": f"{budget_tier.capitalize()} tier dhaba to restaurant prices",
                },
                "accommodation_estimate": {
                    "per_night": {"min": accommodation_per_night[0], "max": accommodation_per_night[1]},
                    "total": {"min": accommodation_per_night[0] * days, "max": accommodation_per_night[1] * days},
                },
                "total_trip": {
                    "transport_only": {"min": transport_total_min, "max": transport_total_max},
                    "with_food_1day": {"min": transport_total_min + food_total_min, "max": transport_total_max + food_total_max},
                    "with_accommodation_1night": {
                        "min": transport_total_min + food_total_min + accommodation_per_night[0],
                        "max": transport_total_max + food_total_max + accommodation_per_night[1],
                    },
                },
                "confidence": "MEDIUM",
                "notes": "Fares are estimates. Cab/auto fares may vary. Train fares are fixed class fares.",
            }
        }
        return result
    except Exception as e:
        logger.error(f"Budget calculation tool error: {e}")
        return {"error": str(e), "budget": None}
