import os
import random
import time
import asyncio
import psutil
from typing import List
from fastapi import FastAPI, Request, Response, HTTPException, Query, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from .logger import setup_logging, logger
from .config import settings
from .database import get_db, engine, Base
from .models import User, Resource as ResourceModel
from .schemas import UserCreate, UserResponse, Token, ResourceCreate, ResourceResponse
from .auth import get_password_hash, verify_password, create_access_token, get_current_user

# Setup Logging
setup_logging()

# Setup OpenTelemetry Instrumentation is done in a separate block if needed, 
# but here we'll keep it simple for brevity, assuming provider is set elsewhere or using defaults.

app = FastAPI(title=settings.PROJECT_NAME)

# Instrumentation
FastAPIInstrumentor.instrument_app(app)

# Prometheus Metrics
REQUEST_COUNT = Counter("http_requests_total", "Total HTTP Requests", ["method", "endpoint", "status"])
REQUEST_LATENCY = Histogram("http_request_duration_seconds", "HTTP Request Latency", ["method", "endpoint"])
ERROR_COUNT = Counter("http_errors_total", "Total HTTP Errors", ["method", "endpoint", "status"])
DB_POOL_SIZE = Counter("db_pool_size", "Database connection pool size") # Placeholder for real pool metrics

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        # In production, use migrations (alembic)
        await conn.run_sync(Base.metadata.create_all)
    logger.info("application_started", version="1.0.0")

@app.middleware("http")
async def observability_middleware(request: Request, call_next):
    start_time = time.time()
    method = request.method
    path = request.url.path
    
    # Failure Injection: Latency
    if random.random() < settings.FAILURE_LATENCY_PROBABILITY:
        inject_latency = random.uniform(1.0, 3.0)
        logger.warning("injecting_latency", duration=inject_latency, path=path)
        await asyncio.sleep(inject_latency)

    # Failure Injection: Random 5xx
    if random.random() < settings.FAILURE_ERROR_PROBABILITY:
        logger.error("injecting_error", path=path)
        ERROR_COUNT.labels(method=method, endpoint=path, status=500).inc()
        return JSONResponse(status_code=500, content={"error": "Injected failure"})

    try:
        response = await call_next(request)
        status_code = response.status_code
    except Exception as e:
        logger.exception("request_failed", path=path, error=str(e))
        status_code = 500
        ERROR_COUNT.labels(method=method, endpoint=path, status=status_code).inc()
        return JSONResponse(status_code=500, content={"error": "Internal Server Error"})

    duration = time.time() - start_time
    REQUEST_COUNT.labels(method=method, endpoint=path, status=status_code).inc()
    REQUEST_LATENCY.labels(method=method, endpoint=path).observe(duration)
    
    return response

# --- Auth Endpoints ---

@app.post("/api/auth/register", response_model=UserResponse)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(User.username == user.username))
    if result.scalars().first():
        throw HTTPException(status_code=400, detail="Username already registered")
    
    hashed_pwd = get_password_hash(user.password)
    db_user = User(username=user.username, email=user.email, hashed_password=hashed_pwd)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@app.post("/api/auth/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(User.username == form_data.username))
    user = result.scalars().first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        throw HTTPException(status_code=401, detail="Incorrect username or password")
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# --- Resource Endpoints ---

@app.get("/api/resource", response_model=List[ResourceResponse])
async def get_resources(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(ResourceModel).filter(ResourceModel.owner_id == current_user.id))
    return result.scalars().all()

@app.post("/api/resource", response_model=ResourceResponse)
async def create_resource(
    resource: ResourceCreate, 
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    db_resource = ResourceModel(**resource.dict(), owner_id=current_user.id)
    db.add(db_resource)
    await db.commit()
    await db.refresh(db_resource)
    
    # Simulate a background task
    background_tasks.add_task(logger.info, "resource_created_background", resource_id=db_resource.id, owner=current_user.username)
    
    return db_resource

# --- SRE Endpoints ---

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/ready")
async def ready(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(select(1))
        return {"status": "ready"}
    except Exception:
        return JSONResponse(status_code=503, content={"status": "not ready", "error": "database unreachable"})

@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/simulate/memory-leak")
async def simulate_memory_leak():
    if not hasattr(app, "leak_list"):
        app.leak_list = []
    logger.warning("simulating_memory_leak")
    app.leak_list.append(" " * (50 * 1024 * 1024))
    mem = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
    return {"message": "Memory leaked", "current_memory_mb": mem}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
