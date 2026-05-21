import logging
from contextlib import asynccontextmanager
 
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
 
 
# ─────────────────────────────────────────
# STARTUP
# ─────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create DB tables if they don't exist yet
    models.Base.metadata.create_all(bind=engine)
    log.info("Database tables ready.")
 
    # Pre-load default query engine
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
 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   
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
 
 
@app.get("/auth/me", tags=["Auth"])
def get_me(current_user: User = Depends(get_current_user)):
    """Returns the currently logged-in user's profile."""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "is_admin": current_user.is_admin,
    }
 