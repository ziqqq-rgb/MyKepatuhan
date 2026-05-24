import logging
from contextlib import asynccontextmanager
import os
 
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
 
from database.db import engine
from database.models import User
from database import models
from routers.login import router as login_router
from routers.register import router as register_router
from auth.utils import get_current_user
from routers.query import router as query_router
from routers.ingest import router as ingest_router
from pipeline.retriever import build_query_engine
from routers.query import query_engine_cache
 
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
 
@asynccontextmanager
async def lifespan(app: FastAPI):
    models.Base.metadata.create_all(bind=engine)

    log.info("Database tables ready.")
    log.info("Loading default query engine...")

    query_engine_cache["default"] = build_query_engine()
    
    log.info("Query engine ready.")
 
    yield
 
app = FastAPI(
    title="MyKepatuhan API",
    description="RAG-powered compliance assistant for Malaysian entrepreneurs",
    version="1.0.0",
    lifespan=lifespan,
)
 
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # set ALLOWED_ORIGINS=https://yourdomain.com in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(login_router)
app.include_router(register_router)
app.include_router(query_router)
app.include_router(ingest_router)
 
@app.get("/health", tags=["System"])
def health():
    return {"status": "ok", "service": "MyKepatuhan API"}
 
 