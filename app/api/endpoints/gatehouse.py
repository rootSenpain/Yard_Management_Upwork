from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.vehicle_log import VehicleLog
from app.models.user import User, UserRole
from app.api.dependencies import require_roles
from app.core.socket_manager import sio

router = APIRouter()

@router.post("/access-log", status_code=status.HTTP_201_CREATED)
async def log_vehicle_access(
    log_data: dict, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.GATEHOUSE]))
):
    """Tesise giren veya çıkan her aracı kaydeder ve WebSocket ile duyurur."""
    new_log = VehicleLog(
        **log_data,
        region_id=current_user.region_id,
        processed_by_id=current_user.id
    )
    db.add(new_log)
    await db.commit()
    
    # Real-time Broadcast: Kapıdaki hareketliliği tüm dashboardlara bildir
    await sio.emit("vehicle:access", {
        "direction": new_log.direction,
        "vehicle_id": new_log.vehicle_id,
        "driver": new_log.driver_name
    }, room=f"region_{new_log.region_id}")
    
    return {"status": "success", "log_id": new_log.id}