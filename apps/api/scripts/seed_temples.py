import asyncio
import json
from datetime import datetime
from pathlib import Path

from sqlalchemy.dialects.postgresql import insert

from app.infrastructure.database.connection import AsyncSessionLocal
from app.infrastructure.database.models import Temple

SEED_FILE = Path(__file__).resolve().parents[1] / "app" / "infrastructure" / "database" / "seeds" / "temples.json"


async def seed_temples() -> None:
    temples = json.loads(SEED_FILE.read_text(encoding="utf-8"))
    async with AsyncSessionLocal() as session:
        for temple in temples:
            temple["last_verified_at"] = datetime.fromisoformat(
                temple["last_verified_at"].replace("Z", "+00:00")
            )
            stmt = insert(Temple).values(**temple)
            stmt = stmt.on_conflict_do_update(
                index_elements=[Temple.id],
                set_={
                    "name": stmt.excluded.name,
                    "lat": stmt.excluded.lat,
                    "lng": stmt.excluded.lng,
                    "city": stmt.excluded.city,
                    "state": stmt.excluded.state,
                    "timings": stmt.excluded.timings,
                    "darshan_info": stmt.excluded.darshan_info,
                    "dress_code": stmt.excluded.dress_code,
                    "is_active": True,
                    "last_verified_at": stmt.excluded.last_verified_at,
                },
            )
            await session.execute(stmt)
        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed_temples())
