from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_
from app.models.task import ShuntTask, TaskStatus
from app.models.dock_door import DockDoor

async def get_gate_to_door_suggestion(db: AsyncSession, region_id: int, trailer_data: dict):
    """
    Parameter-based task matching algorithm.
    Identifies the most suitable (and highest priority) work order that matches 
    the incoming trailer's specifications.
    """
    
    # 1. Fetch pending tasks in the queue that have no assigned trailer (trailer_id IS NULL)
    # Tasks are ordered by Priority (Descending) and Creation Time (Ascending)
    stmt = select(ShuntTask, DockDoor).join(DockDoor, ShuntTask.to_dock_door_id == DockDoor.id)\
        .filter(
            and_(
                ShuntTask.region_id == region_id,
                ShuntTask.status == TaskStatus.QUEUED,
                ShuntTask.trailer_id == None
            )
        ).order_by(ShuntTask.priority.desc(), ShuntTask.created_at.asc())

    result = await db.execute(stmt)
    pending_tasks = result.all()

    for task, door in pending_tasks:
        # 2. Logic for Parameter Matching
        # Evaluates if the incoming trailer meets the specific task requirements
        matches = [
            # Type matching: Accepts any trailer type if req_trailer_type is empty/null
            not task.req_trailer_type or task.req_trailer_type == trailer_data.get('trailer_type'),
            
            # Load status matching: Ensures the task requirements (Loaded/Empty) match the trailer
            task.req_is_loaded is None or task.req_is_loaded == trailer_data.get('is_loaded'),
            
            # Size/Capacity check: Ensures trailer size meets the minimum requirement for the task
            not task.req_min_size or trailer_data.get('size', 0) >= task.req_min_size
        ]

        # If all criteria evaluate to True, this is the optimal dock door suggestion
        if all(matches):
            return {
                "suggested_door_id": door.id,
                "door_number": door.door_number,
                "task_id": task.id,
                "reason": f"Matches pending {task.priority} priority request for {door.door_number}"
            }
            
    # No immediate match found: Trailer can be directed to the designated Yard (parking area)
    return None