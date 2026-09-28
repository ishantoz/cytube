from __future__ import annotations

import asyncio
import json
import threading
from pathlib import Path
from urllib.parse import quote

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from app.extractor import (
    KIND_VALUES,
    PLATFORMS,
    get_formats,
    validate_format_id,
    validate_page_url,
)
from app.jobs import JOBS, DownloadJob, run_download_job

ROOT = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(ROOT / "templates"))

app = FastAPI(title="CyTube", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory=str(ROOT / "static")), name="static")


class JobRequest(BaseModel):
    url: str
    format_id: str
    kind: str
    label: str = Field(default="")


def platform_context(request: Request, platform: str) -> dict:
    spec = PLATFORMS[platform]
    return {
        "request": request,
        "platform": platform,
        "platforms": PLATFORMS,
        "label": spec["label"],
        "placeholder": spec["placeholder"],
        "hint": spec["hint"],
    }


def render(request: Request, name: str, context: dict, status_code: int = 200) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name=name,
        context=context,
        status_code=status_code,
    )


@app.get("/", include_in_schema=False)
def home() -> RedirectResponse:
    return RedirectResponse("/youtube", status_code=307)


@app.post("/{platform}/inspect", response_class=HTMLResponse)
def inspect_media(request: Request, platform: str, url: str = Form(...)) -> HTMLResponse:
    if platform not in PLATFORMS:
        return render(
            request,
            "partials/error.html",
            {"message": "Unknown platform."},
            status_code=404,
        )

    try:
        page_url = validate_page_url(platform, url)
        data = get_formats(page_url)
    except Exception as error:
        return render(
            request,
            "partials/error.html",
            {"message": str(error) or "Could not read that URL."},
        )

    return render(
        request,
        "partials/results.html",
        {
            "platform": platform,
            "page_url": page_url,
            "media": data,
        },
    )


@app.post("/{platform}/jobs")
def create_job(platform: str, body: JobRequest) -> JSONResponse:
    if platform not in PLATFORMS or body.kind not in KIND_VALUES:
        return JSONResponse({"error": "Unknown platform or download type."}, status_code=400)

    try:
        page_url = validate_page_url(platform, body.url)
        format_id = validate_format_id(body.format_id)
    except Exception as error:
        return JSONResponse({"error": str(error)}, status_code=400)

    job = DownloadJob()
    JOBS.add(job)
    threading.Thread(
        target=run_download_job,
        kwargs={
            "job": job,
            "page_url": page_url,
            "format_id": format_id,
            "kind": body.kind,
        },
        daemon=True,
    ).start()
    return JSONResponse({"job_id": job.id, "label": body.label})


@app.post("/jobs/{job_id}/cancel")
def cancel_job(job_id: str) -> JSONResponse:
    job = JOBS.get(job_id)
    if job is None:
        return JSONResponse({"ok": True, "status": "gone"})
    job.request_cancel()
    if job.path is not None:
        JOBS.remove(job_id)
    return JSONResponse({"ok": True})


@app.get("/jobs/{job_id}/events")
async def job_events(job_id: str) -> StreamingResponse:
    job = JOBS.get(job_id)
    if job is None:
        return StreamingResponse(
            iter(['data: {"stage":"error","message":"Job expired.","percent":0}\n\n']),
            media_type="text/event-stream",
        )

    async def generate():
        last_seq = -1
        while True:
            payload = job.snapshot()
            seq = payload.get("_seq", 0)
            if seq != last_seq:
                last_seq = seq
                yield f"data: {json.dumps(payload)}\n\n"
                if payload.get("stage") in {"ready", "error", "cancelled"}:
                    return
            await asyncio.sleep(0.2)

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/jobs/{job_id}/file")
async def stream_job_file(job_id: str) -> StreamingResponse:
    job = JOBS.get(job_id)
    if job is None or job.path is None or not job.path.exists():
        return JSONResponse({"error": "File is no longer available."}, status_code=404)

    path = job.path
    filename = path.name
    size = path.stat().st_size

    async def chunks():
        try:
            with path.open("rb") as handle:
                while True:
                    data = await asyncio.to_thread(handle.read, 64 * 1024)
                    if not data:
                        break
                    if job.cancelled.is_set():
                        break
                    yield data
        finally:
            JOBS.remove(job_id)

    return StreamingResponse(
        chunks(),
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename*=utf-8''{quote(filename)}",
            "Content-Length": str(size),
            "Cache-Control": "no-store",
        },
    )


@app.get("/{platform}", response_class=HTMLResponse)
def platform_page(request: Request, platform: str) -> HTMLResponse:
    if platform not in PLATFORMS:
        return render(
            request,
            "partials/error.html",
            {"message": "Unknown platform."},
            status_code=404,
        )
    return render(request, "platform.html", platform_context(request, platform))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
