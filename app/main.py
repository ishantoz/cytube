from __future__ import annotations

from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.backend.routes import inspect_router, jobs_router
from app.web.routes import router as web_router

WEB_ROOT = Path(__file__).resolve().parent / "web"

app = FastAPI(title="CyTube", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory=str(WEB_ROOT / "static")), name="static")
app.include_router(jobs_router, prefix="/api")
app.include_router(inspect_router, prefix="/api")
app.include_router(web_router)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
