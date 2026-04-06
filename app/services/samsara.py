import asyncio
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.trailer import Trailer
from app.core.database import AsyncSessionLocal
from app.core.socket_manager import sio
from app.core.logging_config import logger

async def fetch_samsara_gps_data():
    """
    Simulates GPS and status data retrieved from the Samsara API.
    In production, this will use httpx to fetch data from the actual Samsara endpoints.
    """
    # Mock data (Simulating incoming external GPS data)
    return [
        {"trailer_number": "TRL-001", "status": "IN_YARD", "is_loaded": True},
        {"trailer_number": "TRL-002", "status": "AT_DOOR", "is_loaded": False}
    ]

async def sync_trailers_background_task():
    """
    Continuous background worker that polls Samsara data and updates the local database.
    Ensures real-time inventory consistency across the yard.
    """
    while True:
        try:
            logger.info("Samsara Sync: Fetching latest GPS and inventory data...")
            
            # 1. Fetch data from external API
            gps_data = await fetch_samsara_gps_data()

            # 2. Compare with local database and update if necessary
            async with AsyncSessionLocal() as db:
                for item in gps_data:
                    result = await db.execute(
                        select(Trailer).filter(Trailer.trailer_number == item['trailer_number'])
                    )
                    trailer = result.scalars().first()
                    
                    # If trailer exists and status/load doesn't match Samsara, UPDATE it
                    if trailer and (trailer.status != item['status'] or trailer.is_loaded != item['is_loaded']):
                        trailer.status = item['status']
                        trailer.is_loaded = item['is_loaded']
                        await db.commit()
                        
                        # 3. REAL-TIME BROADCAST: Notify all clients in the region via WebSocket
                        await sio.emit('trailer:updated', {
                            'id': trailer.id,
                            'trailer_number': trailer.trailer_number,
                            'status': trailer.status,
                            'is_loaded': trailer.is_loaded,
                            'source': 'Samsara_GPS'
                        }, room=f"region_{trailer.region_id}")
                        
                        logger.info(f"Samsara Sync: Trailer {trailer.trailer_number} updated and broadcasted.")

        except Exception as e:
            logger.error(f"Samsara Sync Error: {e}")
        
        # Sleep for 60 seconds to avoid API rate limiting and excessive resource usage
        await asyncio.sleep(60)