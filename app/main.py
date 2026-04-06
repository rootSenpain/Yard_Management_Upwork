import uvicorn
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio
from starlette.exceptions import HTTPException as StarletteHTTPException

# --- IMPORT API ROUTES ---

# This triggers the registration of the socket events (Client -> Server)
from app.api import websockets

# Import endpoint routers
from app.api.endpoints import health, trailers, auth, tasks, yard_checks, reports

# --- IMPORT CORE COMPONENTS ---
from app.core.socket_manager import sio
from app.core.exceptions import global_exception_handler, http_exception_handler
from app.core.logging_config import logger

# --- IMPORT BACKGROUND SERVICES ---
from app.services.samsara import sync_trailers_background_task

# FastAPI Lifecycle: Actions to perform on server startup and shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Log application startup
    logger.info("Application is starting up...")
    
    # Initialize Samsara GPS sync worker on startup
    samsara_task = asyncio.create_task(sync_trailers_background_task())
    logger.info("Samsara Background Task started.")
    
    yield
    
    # Gracefully cancel the background task on shutdown
    samsara_task.cancel()
    logger.info("Samsara Background Task stopped.")
    logger.info("Application is shutting down...")

# Initialize FastAPI Application
app = FastAPI(
    title="Yard Management System API",
    description="Backend service for high-performance logistics Yard Management System.",
    version="1.0.0",
    lifespan=lifespan,
    openapi_url="/openapi.json",  # Burayı ekledik
    docs_url="/docs",            # Burayı ekledik
    redoc_url=None
)

# --- GLOBAL EXCEPTION HANDLERS ---
# Catch and format specific HTTP errors (404, 401, 403, etc.)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
# Catch all unexpected system errors (500 Internal Server Error)
app.add_exception_handler(Exception, global_exception_handler)

# CORS Configuration (Required for Frontend/Cross-Origin access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- REGISTER API ROUTES (ROUTERS) ---
app.include_router(health.router, prefix="/api/v1/health", tags=["Health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(trailers.router, prefix="/api/v1/trailers", tags=["Trailers"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["Work Queues"])
app.include_router(yard_checks.router, prefix="/api/v1/yard-checks", tags=["Yard Audits"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports & Dashboard"])

# Wrap FastAPI with Socket.io (ASGI Integration for Real-time consistency)
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)

# Entry point for running the application
if __name__ == "__main__":
    uvicorn.run("app.main:socket_app", host="0.0.0.0", port=8000, reload=True)