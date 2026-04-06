from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional

from app.core.database import get_db
from app.models.trailer import Trailer
from app.models.user import User, UserRole
from app.schemas.trailer import TrailerCreate, TrailerResponse

# Servis ve WebSocket bileşenleri
from app.core.socket_manager import sio
from app.api.dependencies import get_current_user, require_roles
from app.services.dispatch_logic import get_gate_to_door_suggestion # Algoritma motoru

router = APIRouter()

@router.post("/", response_model=TrailerResponse, status_code=status.HTTP_201_CREATED)
async def create_trailer(
    trailer_in: TrailerCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.GATEHOUSE]))
):
    """
    Create new trailer (Gate-in) and automatically suggest a dock door if a match exists.
    """
    # 1. Dorsenin sistemde zaten var olup olmadığını kontrol et
    result = await db.execute(select(Trailer).filter(Trailer.trailer_number == trailer_in.trailer_number))
    existing_trailer = result.scalars().first()
    
    if existing_trailer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trailer with this number already exists in the system."
        )

    # 2. Yeni dorse nesnesini oluştur (Yeni eklediğimiz type, size vb. alanlar trailer_in içinde olmalı)
    new_trailer = Trailer(**trailer_in.model_dump())
    new_trailer.region_id = current_user.region_id # Multi-tenant güvenlik
    
    db.add(new_trailer)
    await db.commit()
    await db.refresh(new_trailer)

    # 3. --- AUTO-SUGGESTION ALGORİTMASINI TETİKLE ---
    # İçeri giren dorsenin özelliklerine göre uygun rampa var mı bakıyoruz
    suggestion = await get_gate_to_door_suggestion(
        db, 
        current_user.region_id, 
        trailer_in.model_dump()
    )

    # 4. --- WEBSOCKET BROADCAST ---
    # Sahadaki tüm operatörlere yeni dorseyi ve varsa önerilen rampayı bildir
    room_name = f"region_{new_trailer.region_id}"
    await sio.emit(
        'trailer:created', 
        {
            'id': new_trailer.id,
            'trailer_number': new_trailer.trailer_number,
            'status': new_trailer.status,
            'created_by': current_user.username,
            'suggestion': suggestion # Eğer rampa önerisi varsa burada gidecek
        }, 
        room=room_name
    )
    
    # API yanıtına öneriyi ekle
    setattr(new_trailer, "suggestion", suggestion)
    return new_trailer

@router.get("/", response_model=List[TrailerResponse])
async def get_all_trailers(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve all trailers currently in the system for the user's region.
    """
    # Multi-tenant: Sadece kullanıcının kendi bölgesindeki dorseleri getir
    result = await db.execute(
        select(Trailer).filter(Trailer.region_id == current_user.region_id)
    )
    trailers = result.scalars().all()
    return trailers