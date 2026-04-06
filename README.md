🚛 Yard Management System (YMS) Backend API

This is a production-grade, multi-tenant Yard Management System built to handle real-time logistics operations. It manages trailer movements, dock door assignments, yard driver tasks, and automated GPS syncing with Samsara.

🚀 Tech Stack

Framework: FastAPI (Python 3.11+)
Database: PostgreSQL with SQLAlchemy (Async)
Migrations: Alembic
Real-time: Socket.io (ASGI)
Task Queue: Background Tasks for Samsara GPS Polling
Deployment: Docker & Docker-Compose with Nginx Reverse Proxy

🛠 Features & Module Specs

Multi-tenancy: Data isolation using region_id across all 18+ tables.
RBAC (Role-Based Access Control): Granular permissions for 7 roles (Admin, Super User, Dispatch, Warehouse, Gatehouse, Driver, Reporting).
Task State Machine: Strict lifecycle for shunt tasks: QUEUED → ASSIGNED → ACCEPTED → PINNED → COMPLETED.
Gate-to-Door Auto-suggestion: Intelligent parameter-based matching for incoming trailers.
Samsara Integration: Automated GPS polling and yard inventory updates.
Reporting: Dashboard statistics and CSV export functionality for yard audits.

📦 Getting Started (Docker Deployment)

1.Clone the repository:
git clone <repository-url>
cd yard-management-system/Server


2.Configure Environment Variables:
Create a .env file in the root directory:
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_NAME=yms_db
SECRET_KEY=your_super_secret_jwt_key
ALGORITHM=HS256

3.Deploy with One Command:
Bash: 
docker-compose up --build


4.Access API Documentation:
Open http://localhost/docs for Swagger UI.


📡 WebSocket Event Registry (Server to Client)
Join the room region_{id} to start receiving the following events:

trailer:created

Payload: {"id": 10, "trailer_number": "TRL-001", "suggestion": {...}}

Description: Broadcast when a new trailer is gated in. Includes auto-suggestion data.

task:created

Payload: {"id": 5, "priority": 10, "type": "PULL"}

Description: Notifies all drivers in the region of a new high-priority task.

task:updated

Payload: {"task_id": 5, "status": "PINNED"}

Description: Real-time update on every state machine transition (Accepted, Pinned, etc.).

vehicle:access

Payload: {"direction": "IN", "driver": "John Doe"}

Description: Real-time log of gatehouse activity for dashboard monitoring.

audit:started

Payload: {"id": 1, "created_by": "admin"}

Description: Alerts the team that a physical Yard Check session has begun.