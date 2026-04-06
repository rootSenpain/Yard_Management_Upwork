import logging
from app.core.socket_manager import sio

# Initialize logger for real-time event tracking
logger = logging.getLogger(__name__)

@sio.event
async def connect(sid, environ):
    """
    Triggered when a new client (Driver, Dispatcher, or Admin) 
    establishes a WebSocket connection.
    """
    logger.info(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    """
    Triggered when a client closes the connection or loses network.
    """
    logger.info(f"Client disconnected: {sid}")

@sio.on("join_region")
async def handle_join_region(sid, data):
    """
    Implements the 'room-per-region' pattern.
    Clients must join a specific room based on their region_id to receive 
    isolated real-time updates for their facility.
    
    Payload expected: {"region_id": int}
    """
    region_id = data.get("region_id")
    
    if region_id:
        room_name = f"region_{region_id}"
        await sio.enter_room(sid, room_name)
        
        # Acknowledge success back to the specific client
        await sio.emit(
            "subscription_success", 
            {"message": f"Successfully joined room: {room_name}", "room": room_name}, 
            to=sid
        )
        logger.info(f"SID {sid} joined room: {room_name}")
    else:
        # Send error if region_id is missing or invalid
        await sio.emit(
            "subscription_error", 
            {"message": "Failed to join room: region_id is required."}, 
            to=sid
        )
        logger.warning(f"Join attempt failed for SID {sid}: No region_id provided.")

@sio.on("driver:status_update")
async def handle_driver_status(sid, data):
    """
    Handles real-time status updates directly from the driver's mobile app.
    Can be used for manual GPS pings or availability toggles.
    """
    # Potential logic for manual driver tracking outside of Samsara
    logger.info(f"Driver status update from {sid}: {data}")
    pass