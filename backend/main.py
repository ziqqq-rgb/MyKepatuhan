import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from core import config
from core.rate_limit import limiter
from database.db import engine
from database import models
from routers.login import router as login_router
from routers.register import router as register_router
from routers.query import router as query_router
from routers.ingest import router as ingest_router
from routers.conversations import router as conversations_router
from services.rag_pipeline import warm_up


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    models.Base.metadata.create_all(bind=engine)
    log.info("Database tables ready.")
    log.info("Warming up RAG pipeline...")
    warm_up()
    log.info("RAG pipeline ready.")
    yield


app = FastAPI(
    title="MyKepatuhan API",
    description="RAG-powered compliance assistant for Malaysian entrepreneurs",
    version="1.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    log.error(f"Unhandled exception on {request.method} {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected internal server error occurred."},
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(login_router)
app.include_router(register_router)
app.include_router(query_router)
app.include_router(ingest_router)
app.include_router(conversations_router)


@app.get("/health", tags=["System"])
def health():
    return {"status": "ok", "service": "MyKepatuhan API"}