from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_trips():
    return {"message": "Trips endpoint stub"}
