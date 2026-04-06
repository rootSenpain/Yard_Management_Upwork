from app.core.database import Base
from app.models.trailer import Trailer
from app.models.user import User
from app.models.dock_door import DockDoor
from app.models.task import ShuntTask
from app.models.vehicle import Vehicle      
from app.models.vehicle_log import VehicleLog 
from app.models.yard_check import YardCheck, YardCheckItem
# As you create new models, import them here