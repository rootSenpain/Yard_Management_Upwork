# 🚛 Yard Management System (YMS) Backend API

This is a production-grade, multi-tenant Yard Management System built to handle real-time logistics operations. It manages trailer movements, dock door assignments, yard driver tasks, and automated GPS syncing with Samsara.

## 🚀 Tech Stack

* **Framework:** FastAPI (Python 3.11+)
* **Database:** PostgreSQL with SQLAlchemy (Async)
* **Migrations:** Alembic
* **Real-time:** Socket.io (ASGI)
* **Task Queue:** Background Tasks for Samsara GPS Polling
* **Deployment:** Docker & Docker-Compose with Nginx Reverse Proxy

## 🛠 Features & Module Specs

* **Multi-tenancy:** Data isolation using `region_id` across all 18+ tables.
* **RBAC (Role-Based Access Control):** Granular permissions for 7 roles (Admin, Super User, Dispatch, Warehouse, Gatehouse, Driver, Reporting).
* **Task State Machine:** Strict lifecycle for shunt tasks: `QUEUED → ASSIGNED → ACCEPTED → PINNED → COMPLETED`.
* **Gate-to-Door Auto-suggestion:** Intelligent parameter-based matching for incoming trailers.
* **Samsara Integration:** Automated GPS polling and yard inventory updates.
* **Reporting:** Dashboard statistics and CSV export functionality for yard audits.

## 📦 Getting Started (Docker Deployment)

### 1. Clone the repository
```bash
git clone <repository-url>
cd yard-management-system/Server
```

### 2. Configure Environment Variables
```Code snippets
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_NAME=yms_db
SECRET_KEY=your_super_secret_jwt_key
ALGORITHM=HS256
```

### 3. Deploy with One Command
```bash
docker-compose up --build
```
### 4. Access API Documentation
```
Open http://localhost/docs in your browser for the Swagger UI.

## 🔌 Core API Endpoints

The API is fully documented using OpenAPI (Swagger). Below are the core operational endpoints for the Yard Management flow:

### Authentication
* `POST /api/v1/auth/login` - Authenticate user and receive JWT Bearer token.

### Trailer Management
* `GET /api/v1/trailers` - Retrieve all trailers in the yard (supports filtering by status/region).
* `POST /api/v1/trailers` - Manually gate-in a new trailer.
* `GET /api/v1/trailers/suggest-door` - AI-driven endpoint that suggests the optimal dock door based on trailer type and current yard congestion.

### Task Dispatch & State Machine
* `POST /api/v1/tasks/dispatch` - Create a new shunt task (Queued).
* `POST /api/v1/tasks/{task_id}/assign/{driver_id}` - Assign a queued task to a specific yard driver.
* `PATCH /api/v1/tasks/{task_id}/transition` - Advance the task state. 
  * *Required parameter:* `new_status` (ACCEPTED, PINNED, COMPLETED, etc.)

---

## 🔄 Strict Task State Machine

The core of the YMS is a strictly enforced state machine for all yard tasks. The API will reject any invalid transitions (e.g., jumping from `QUEUED` directly to `COMPLETED`), ensuring absolute data integrity.


[QUEUED] ──(Dispatcher)──> [ASSIGNED] ──(Driver)──> [ACCEPTED]
                                                          │
                                                          v
[COMPLETED] <──(Gate/Dock)── [PINNED] <──(Movement)───────┘

```

### 🛠️ Local Development & Troubleshooting
```bash
docker logs -f yms_api
```

### Manual Database Migrations (If adding new models)
```bash
docker exec -it yms_api alembic revision --autogenerate -m "Description"
docker exec -it yms_api alembic upgrade head
```

### Resetting the Database (Wiping volumes for a fresh start)
```bash
docker-compose down -v
docker-compose up --build
```

### 🛡️ License & Contact
This is a proprietary backend system designed for high-availability logistics operations. Developed by Ali Yılmaz - Computer and Cyber Security Engineer.

