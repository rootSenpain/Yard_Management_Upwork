import csv
import io
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from app.core.database import get_db
from app.models.trailer import Trailer
from app.models.task import ShuntTask, TaskStatus
from app.models.user import User, UserRole
from app.api.dependencies import require_roles

router = APIRouter()

@router.get("/summary", tags=["Dashboard"])
async def get_dashboard_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.REPORTING]))
):
    """
    Dashboard widget'ları için genel istatistikleri döner.
    """
    # 1. Toplam Dorse Sayısı (Mevcut bölgede)
    total_trailers = await db.execute(
        select(func.count(Trailer.id)).filter(Trailer.region_id == current_user.region_id)
    )
    
    # 2. Tamamlanan Görev Sayısı (Son 24 saat)
    last_24h = datetime.now() - timedelta(hours=24)
    completed_tasks = await db.execute(
        select(func.count(ShuntTask.id))
        .filter(ShuntTask.region_id == current_user.region_id)
        .filter(ShuntTask.status == TaskStatus.COMPLETED)
        .filter(ShuntTask.updated_at >= last_24h)
    )

    # 3. Yüklü vs Boş Oranı
    loaded_count = await db.execute(
        select(func.count(Trailer.id))
        .filter(Trailer.region_id == current_user.region_id)
        .filter(Trailer.is_loaded == True)
    )

    return {
        "active_trailers": total_trailers.scalar(),
        "completed_tasks_24h": completed_tasks.scalar(),
        "loaded_trailers": loaded_count.scalar(),
        "timestamp": datetime.now()
    }

@router.get("/export/trailers/csv")
async def export_trailers_csv(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.REPORTING]))
):
    """
    Mevcut sahadaki tüm dorselerin envanterini CSV olarak indirir.
    """
    result = await db.execute(
        select(Trailer).filter(Trailer.region_id == current_user.region_id)
    )
    trailers = result.scalars().all()

    # Bellek üzerinde bir CSV dosyası oluşturuyoruz
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Başlıklar
    writer.writerow(["ID", "Trailer Number", "Status", "Is Loaded", "Type", "Created At"])
    
    # Veriler
    for t in trailers:
        writer.writerow([t.id, t.trailer_number, t.status, t.is_loaded, t.trailer_type, t.created_at])

    # Dosya akışını başlat (StreamingResponse)
    output.seek(0)
    filename = f"yard_inventory_{datetime.now().strftime('%Y%m%d')}.csv"
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )