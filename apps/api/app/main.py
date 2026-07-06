from fastapi import FastAPI

app = FastAPI(
    title="TravelMate AI API",
    version="1.0.0",
    description="Backend API for TravelMate AI"
)

@app.get("/health/ready")
async def health_ready():
    return {"status": "healthy"}
