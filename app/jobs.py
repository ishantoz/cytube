from __future__ import annotations

import shutil
import tempfile
import threading
import time
import uuid
from pathlib import Path
from typing import Any

import yt_dlp

from app.extractor import ydl_download_options


def format_speed(speed: float | None) -> str | None:
    if not speed:
        return None
    units = ("B/s", "KB/s", "MB/s", "GB/s")
    value = float(speed)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.1f} {unit}"
        value /= 1024
    return None


def format_eta(seconds: Any) -> str | None:
    if seconds is None:
        return None
    try:
        total = max(0, int(seconds))
    except (TypeError, ValueError):
        return None
    minutes, secs = divmod(total, 60)
    if minutes > 99:
        return "—"
    return f"{minutes}:{secs:02d}"


class DownloadJob:
    def __init__(self) -> None:
        self.id = uuid.uuid4().hex
        self.lock = threading.Lock()
        self.seq = 0
        self.payload: dict[str, Any] = {
            "stage": "queued",
            "percent": 0,
            "message": "Queued…",
            "speed": None,
            "eta": None,
            "filename": None,
            "size": None,
        }
        self.temp_dir: Path | None = None
        self.path: Path | None = None
        self.created_at = time.time()
        self.consumed = False
        self.cancelled = threading.Event()

    def request_cancel(self) -> None:
        if self.cancelled.is_set():
            return
        self.cancelled.set()
        self.emit(
            stage="cancelled",
            percent=0,
            message="Cancelled.",
            speed=None,
            eta=None,
        )

    def _raise_if_cancelled(self) -> None:
        if self.cancelled.is_set():
            raise yt_dlp.utils.DownloadCancelled("Cancelled by user")

    def snapshot(self) -> dict[str, Any]:
        with self.lock:
            payload = dict(self.payload)
            payload["_seq"] = self.seq
            return payload

    def emit(self, **fields: Any) -> None:
        with self.lock:
            self.payload.update(fields)
            self.seq += 1

    def progress_hook(self, data: dict[str, Any]) -> None:
        self._raise_if_cancelled()
        status = data.get("status")
        if status == "downloading":
            total = data.get("total_bytes") or data.get("total_bytes_estimate") or 0
            downloaded = data.get("downloaded_bytes") or 0
            percent = int(downloaded * 80 / total) if total else 5
            self.emit(
                stage="downloading",
                percent=min(percent, 80),
                message="Fetching media on the server…",
                speed=format_speed(data.get("speed")),
                eta=format_eta(data.get("eta")),
            )
        elif status == "finished":
            self.emit(
                stage="processing",
                percent=85,
                message="Processing with FFmpeg…",
                speed=None,
                eta=None,
            )

    def postprocessor_hook(self, data: dict[str, Any]) -> None:
        self._raise_if_cancelled()
        status = data.get("status")
        if status == "started":
            self.emit(
                stage="processing",
                percent=88,
                message="Merging tracks…",
            )
        elif status == "finished":
            self.emit(
                stage="processing",
                percent=92,
                message="Preparing the stream…",
            )

    def destroy(self) -> None:
        if self.temp_dir is not None:
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            self.temp_dir = None
        self.path = None


class JobStore:
    def __init__(self) -> None:
        self._jobs: dict[str, DownloadJob] = {}
        self._lock = threading.Lock()

    def add(self, job: DownloadJob) -> None:
        self.purge()
        with self._lock:
            self._jobs[job.id] = job

    def get(self, job_id: str) -> DownloadJob | None:
        with self._lock:
            return self._jobs.get(job_id)

    def remove(self, job_id: str) -> None:
        with self._lock:
            job = self._jobs.pop(job_id, None)
        if job is not None:
            job.destroy()

    def purge(self) -> None:
        now = time.time()
        expired: list[str] = []
        with self._lock:
            for job_id, job in self._jobs.items():
                if now - job.created_at > 900:
                    expired.append(job_id)
        for job_id in expired:
            self.remove(job_id)


JOBS = JobStore()


def run_download_job(
    job: DownloadJob,
    *,
    page_url: str,
    format_id: str,
    kind: str,
) -> None:
    try:
        job.emit(stage="starting", percent=2, message="Starting download…")
        job.temp_dir = Path(tempfile.mkdtemp(prefix="cytube-"))
        options = ydl_download_options(
            kind=kind,
            format_id=format_id,
            outtmpl=str(job.temp_dir / "%(title).80B [%(id)s].%(ext)s"),
        )
        options["progress_hooks"] = [job.progress_hook]
        options["postprocessor_hooks"] = [job.postprocessor_hook]
        options["noprogress"] = True

        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([page_url])

        job._raise_if_cancelled()

        files = [path for path in job.temp_dir.iterdir() if path.is_file()]
        if not files:
            raise RuntimeError("Download finished but no file was written.")
        job.path = max(files, key=lambda path: path.stat().st_size)
        size = job.path.stat().st_size
        job.emit(
            stage="ready",
            percent=94,
            message="Streaming to your device…",
            filename=job.path.name,
            size=size,
        )
    except yt_dlp.utils.DownloadCancelled:
        job.emit(
            stage="cancelled",
            percent=0,
            message="Cancelled.",
        )
        job.destroy()
    except Exception as error:
        if job.cancelled.is_set():
            job.emit(stage="cancelled", percent=0, message="Cancelled.")
        else:
            job.emit(
                stage="error",
                percent=0,
                message=str(error) or "Download failed.",
            )
        job.destroy()
