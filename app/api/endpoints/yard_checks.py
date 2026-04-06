from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.core.database import get_db
from app.models.yard_check import YardCheck, YardCheckItem, AuditStatus
from app.models.user import User, UserRole
from app.api.dependencies import get_current_user, require_roles
from app.core.socket_manager import sio

router = APIRouter()

@router.post("/start", status_code=status.HTTP_201_CREATED)
async def start_yard_check(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.SUPER_USER, UserRole.REPORTING]))
):
    """Yeni bir saha denetim seansı başlatır."""
    new_check = YardCheck(region_id=current_user.region_id, created_by_id=current_user.id)
    db.add(new_check)
    await db.commit()
    await db.refresh(new_check)
    
    await sio.emit("audit:started", {"id": new_check.id}, room=f"region_{new_check.region_id}")
    return new_check

@router.post("/{check_id}/verify/{trailer_id}")
async def verify_trailer(
    check_id: int,
    trailer_id: int,
    audit_status: AuditStatus,
    notes: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Bir dorseyi denetim listesinde işaretler."""
    item = YardCheckItem(
        yard_check_id=check_id,
        trailer_id=trailer_id,
        status=audit_status,
        notes=notes
    )
    db.add(item)
    await db.commit()
    return {"status": "item_logged"}

@router.get("/{check_id}/summary")
async def get_audit_summary(check_id: int, db: AsyncSession = Depends(get_db)):
    """Denetimin özet raporunu döner (Verify/Fix/Missing sayıları)."""
    # Her durumdan kaçar tane var sayalım
    result = await db.execute(
        select(YardCheckItem.status, func.count(YardCheckItem.id))
        .filter(YardCheckItem.yard_check_id == check_id)
        .group_by(YardCheckItem.status)
    )
    summary = {row[0]: row[1] for row in result.all()}
    return {"yard_check_id": check_id, "counts": summary}