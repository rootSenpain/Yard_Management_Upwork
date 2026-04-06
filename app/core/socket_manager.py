import socketio

# Initialize the Async Server instance
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')

@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")

@sio.event
async def join_region(sid, data):
    """
    Client must emit this event to join a specific region's room.
    Payload example: {"region_id": 1}
    """
    region_id = data.get("region_id")
    if region_id:
        room_name = f"region_{region_id}"
        sio.enter_room(sid, room_name)
        print(f"Client {sid} joined room: {room_name}")
        await sio.emit('system_message', {'message': f'Successfully joined {room_name}'}, room=sid)

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")