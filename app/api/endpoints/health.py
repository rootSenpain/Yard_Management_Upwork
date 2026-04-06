from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def health_check():
    """Check if the API is running correctly."""
    return {
        "status": "success",
        "message": "Yard Management System API is running successfully!"
    }