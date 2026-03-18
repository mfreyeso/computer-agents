from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.endpoints.sessions import router as sessions_router
from src.api.endpoints.websockets import router as websockets_router
from src.core.config import settings
from src.core.logging import logger
from src.database.session import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create DB tables (in production, use alembic)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Cleanup logic if any
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sessions_router)
app.include_router(websockets_router)

@app.get("/health")
async def health_check():
    logger.info("Health check pinged")
    return {"status": "ok"}
