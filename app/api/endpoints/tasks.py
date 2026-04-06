from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from sqlalchemy import func

from app.core.database import get_db
from app.models.task import ShuntTask, TaskStatus
from app.models.trailer import Trailer
from app.models.user import User, UserRole
from app.schemas.task import TaskCreate, TaskResponse
from app.api.dependencies import get_current_user, require_roles
from app.core.socket_manager import sio

router = APIRouter()

@router.post("/dispatch", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_in: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.DISPATCH]))
):
    """
    Creates a new Shunt Task and adds it to the queue in QUEUED status.
    Requires Admin or Dispatch role.
    """
    new_task = ShuntTask(
        **task_in.model_dump(),
        region_id=current_user.region_id,
        created_by_id=current_user.id,
        status=TaskStatus.QUEUED
    )
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)

    # WebSocket: Broadcast the new task to the entire region
    await sio.emit("task:created", {
        "id": new_task.id, 
        "priority": new_task.priority,
        "type": new_task.task_type
    }, room=f"region_{new_task.region_id}")
    
    return new_task

@router.post("/{task_id}/assign/{driver_id}")
async def assign_task(
    task_id: int,
    driver_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.DISPATCH]))
):
    """
    Manually assigns a task to a specific driver (Transitions QUEUED -> ASSIGNED).
    """
    result = await db.execute(select(ShuntTask).filter(ShuntTask.id == task_id))
    task = result.scalars().first()
    
    if not task or task.status != TaskStatus.QUEUED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Task is not available for assignment"
        )
        
    task.assigned_driver_id = driver_id
    task.status = TaskStatus.ASSIGNED
    await db.commit()
    
    # Real-time update for dispatchers and drivers
    await sio.emit("task:assigned", {
        "task_id": task.id, 
        "driver_id": driver_id
    }, room=f"region_{task.region_id}")
    
    return {"message": f"Task {task_id} assigned to driver {driver_id}"}

@router.patch("/{task_id}/transition", response_model=TaskResponse)
async def transition_task_status(
    task_id: int,
    new_status: TaskStatus,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Strict State Machine Implementation:
    ASSIGNED -> ACCEPTED -> PINNED -> COMPLETED
    Includes branching for REJECTED tasks.
    """
    result = await db.execute(select(ShuntTask).filter(ShuntTask.id == task_id))
    task = result.scalars().first()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    current_status = task.status

    # --- STATE MACHINE TRANSITION RULES ---
    
    # 1. Driver accepts the assigned task
    if new_status == TaskStatus.ACCEPTED:
        if current_status != TaskStatus.ASSIGNED:
            raise HTTPException(status_code=400, detail="Must be ASSIGNED before it can be ACCEPTED")
        if task.assigned_driver_id != current_user.id:
            raise HTTPException(status_code=403, detail="Only the assigned driver can accept this task")

    # 2. Driver hooks/pins the trailer
    elif new_status == TaskStatus.PINNED:
        if current_status != TaskStatus.ACCEPTED:
            raise HTTPException(status_code=400, detail="Must be ACCEPTED before it can be PINNED")

    # 3. Task completion and trailer relocation
    elif new_status == TaskStatus.COMPLETED:
        if current_status != TaskStatus.PINNED:
            raise HTTPException(status_code=400, detail="Must be PINNED before it can be COMPLETED")
        
        # AUTOMATION: Automatically update trailer status and location upon task completion
        if task.trailer_id:
            trailer_res = await db.execute(select(Trailer).filter(Trailer.id == task.trailer_id))
            trailer = trailer_res.scalars().first()
            if trailer:
                # Set status based on destination (Dock or Yard)
                trailer.status = "AT_DOOR" if task.to_dock_door_id else "IN_YARD"
                # Update timestamp for audit tracking (Verify/Fix logic)
                trailer.updated_at = func.now()

    # 4. Handle Rejected tasks
    elif new_status == TaskStatus.REJECTED:
        if current_status != TaskStatus.ASSIGNED:
            raise HTTPException(status_code=400, detail="Only assigned tasks can be rejected")
        
        # Rejected tasks return to QUEUED status and float to the top of the work queue
        task.assigned_driver_id = None
        new_status = TaskStatus.QUEUED
        task.priority = min(task.priority + 1, 10) # Increase priority level

    # Apply changes to the database
    task.status = new_status
    await db.commit()
    await db.refresh(task)

    # WebSocket: Notify all connected clients about the state change
    await sio.emit("task:updated", {
        "task_id": task.id, 
        "status": task.status,
        "trailer_id": task.trailer_id
    }, room=f"region_{task.region_id}")
    
    return task