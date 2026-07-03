"""
Shared pytest setup.

Two problems this solves:

1. `core/config.py` calls `get_env_or_fail()` at import time. Any test
   that imports a backend module (even indirectly) crashes during
   collection unless required env vars already exist. We set safe
   dummy values here, before pytest imports any test file.

2. Backend modules import as `from pipeline...`, `from core...` etc.
   (no `backend.` prefix), so `backend/` must be on sys.path. This
   makes tests runnable from the repo root or from `backend/` itself.
"""
import os
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

_REQUIRED_ENV_DEFAULTS = {
    "GEMINI_KEY": "test-gemini-key",
    "PINECON_KEY": "test-pinecone-key",
    "JWT_SECRET_KEY": "test-jwt-secret",
    "DATABASE_URL": "sqlite:///:memory:",
    "STACK_PROJECT_ID": "test-stack-project",
    "STACK_SECRET_SERVER_KEY": "test-stack-secret",
}

for _key, _value in _REQUIRED_ENV_DEFAULTS.items():
    os.environ.setdefault(_key, _value)