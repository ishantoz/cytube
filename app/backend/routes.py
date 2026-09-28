from __future__ import annotations

import asyncio
import json
import threading
from urllib.parse import quote

from fastapi import APIRouter
from fastapi.responses import JSONResponse, Response, StreamingResponse

from app.backend.schemas import InspectRequest, JobRequest
from app.logic.extractor import (
    KIND_VALUES,
    PLATFORMS,
    get_formats,
    validate_format_id,
    validate_page_url,
)
from app.logic.jobs import JOBS, DownloadJob, run_download_job

jobs_router = APIRouter()
inspect_router = APIRouter()


@inspect_router.post("/{platform}/inspect")
def inspect_media(platform: str, body: InspectRequest) -> JSONResponse:
    if platform not in PLATFORMS:
        return JSONResponse({"error": "Unknown platform."}, status_code=404)

    try:
        page_url = validate_page_url(platform, body.url)
        media = get_formats(page_url)
    except Exception as error:
        return JSONResponse({"error": str(error) or "Could not read that URL."}, status_code=400)

    return JSONResponse({"page_url": page_url, "media": media})


@jobs_router.post("/{platform}/jobs")
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


@jobs_router.post("/jobs/{job_id}/cancel")
def cancel_job(job_id: str) -> JSONResponse:
    job = JOBS.get(job_id)
    if job is None:
        return JSONResponse({"ok": True, "status": "gone"})
    job.request_cancel()
    if job.path is not None:
        JOBS.remove(job_id)
    return JSONResponse({"ok": True})


@jobs_router.get("/jobs/{job_id}/events")
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


@jobs_router.get("/jobs/{job_id}/file")
async def stream_job_file(job_id: str) -> Response:
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
