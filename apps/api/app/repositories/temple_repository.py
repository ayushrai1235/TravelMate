from decimal import Decimal
from typing import Any

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models import Temple


class TempleRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, temple_id: str) -> dict[str, Any] | None:
        temple = await self.db.get(Temple, temple_id)
        if temple is None or not temple.is_active:
            return None
        return serialize_temple(temple)

    async def search(self, query: str | None = None, city: str | None = None, limit: int = 10) -> list[dict[str, Any]]:
        stmt: Select[tuple[Temple]] = select(Temple).where(Temple.is_active.is_(True)).limit(min(limit, 50))
        if query:
            stmt = stmt.where(Temple.name.ilike(f"%{query}%"))
        if city:
            stmt = stmt.where(Temple.city.ilike(f"%{city}%"))
        result = await self.db.execute(stmt)
        return [serialize_temple(row) for row in result.scalars().all()]


def serialize_temple(temple: Temple) -> dict[str, Any]:
    return {
        "id": temple.id,
        "name": temple.name,
        "lat": to_float(temple.lat),
        "lng": to_float(temple.lng),
        "city": temple.city,
        "state": temple.state,
        "timings": temple.timings,
        "darshan_info": temple.darshan_info,
        "dress_code": temple.dress_code,
        "is_active": temple.is_active,
        "last_verified_at": temple.last_verified_at.isoformat() if temple.last_verified_at else None,
        "source": "temple_database",
        "confidence": "HIGH",
    }


def to_float(value: Decimal | float | None) -> float | None:
    return float(value) if value is not None else None
