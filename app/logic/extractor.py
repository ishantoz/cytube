from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse

import yt_dlp
from yt_dlp.networking.impersonate import ImpersonateTarget

PLATFORMS: dict[str, dict[str, Any]] = {
    "youtube": {
        "label": "YouTube",
        "hosts": ("youtube.com", "youtu.be"),
        "placeholder": "https://www.youtube.com/watch?v=…",
        "hint": "Public YouTube videos only. Playlists are not supported.",
    },
    "instagram": {
        "label": "Instagram",
        "hosts": ("instagram.com",),
        "placeholder": "https://www.instagram.com/reel/…",
        "hint": "Public reels and posts only. Login-walled media needs cookies and is not supported.",
    },
    "facebook": {
        "label": "Facebook",
        "hosts": ("facebook.com", "fb.watch", "fb.com"),
        "placeholder": "https://www.facebook.com/… or https://fb.watch/…",
        "hint": "Public Facebook videos only. Private or login-walled posts are not supported.",
    },
    "tiktok": {
        "label": "TikTok",
        "hosts": ("tiktok.com",),
        "placeholder": "https://www.tiktok.com/@user/video/…",
        "hint": "Public TikTok videos only. Login-walled or region-locked posts are not supported.",
    },
    "dailymotion": {
        "label": "Dailymotion",
        "hosts": ("dailymotion.com", "dai.ly"),
        "placeholder": "https://www.dailymotion.com/video/…",
        "hint": "Public Dailymotion videos only. Private videos are not supported.",
    },
    "bilibili": {
        "label": "Bilibili",
        "hosts": ("bilibili.com", "bilibili.tv", "b23.tv"),
        "placeholder": "https://www.bilibili.com/video/… or https://www.bilibili.tv/…",
        "hint": "Public Bilibili videos only. Login-walled or region-locked posts are not supported.",
    },
}

FORMAT_ID_RE = re.compile(r"^[\w.-]+$")
KIND_VALUES = frozenset({"merged", "video", "audio", "extract_audio"})
FIREFOX = ImpersonateTarget("firefox")

_YDL_BASE = {
    "quiet": True,
    "no_warnings": True,
    "noplaylist": True,
    "skip_download": True,
    "impersonate": FIREFOX,
}


def hostname_allowed(url: str, hosts: tuple[str, ...]) -> bool:
    parsed = urlparse(url.strip())
    if parsed.scheme not in ("http", "https"):
        return False
    hostname = (parsed.hostname or "").lower().removeprefix("www.")
    return any(
        hostname == host or hostname.endswith(f".{host}")
        for host in hosts
    )


def validate_page_url(platform: str, url: str) -> str:
    spec = PLATFORMS.get(platform)
    if spec is None:
        raise ValueError("Unknown platform.")
    cleaned = url.strip()
    if not cleaned:
        raise ValueError("Paste a video URL first.")
    if not hostname_allowed(cleaned, spec["hosts"]):
        raise ValueError(
            f"That does not look like a public {spec['label']} URL."
        )
    return cleaned


def validate_format_id(format_id: str) -> str:
    if not FORMAT_ID_RE.fullmatch(format_id or ""):
        raise ValueError("Invalid format.")
    return format_id


def format_size(num: Any) -> str | None:
    if not num:
        return None
    try:
        value = float(num)
    except (TypeError, ValueError):
        return None
    units = ("B", "KB", "MB", "GB")
    for unit in units:
        if value < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(value)} {unit}"
            return f"{value:.1f} {unit}"
        value /= 1024
    return None


def format_duration(seconds: Any) -> str:
    if seconds is None:
        return "—"
    try:
        total = int(float(seconds))
    except (TypeError, ValueError):
        return "—"
    hours, rem = divmod(total, 3600)
    minutes, secs = divmod(rem, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def get_formats(url: str) -> dict[str, Any]:
    with yt_dlp.YoutubeDL(_YDL_BASE) as ydl:
        info = ydl.extract_info(url, download=False)

    if not info:
        raise ValueError(
            "Nothing was returned. The post may be private or login-walled."
        )

    if info.get("_type") == "playlist":
        raise ValueError(
            "Playlists are not supported. Paste a single video or post URL."
        )

    formats = info.get("formats") or []
    title = info.get("title") or "video"

    audio_only = [
        fmt
        for fmt in formats
        if fmt.get("vcodec") in (None, "none")
        and fmt.get("acodec") not in (None, "none")
        and fmt.get("url")
        and fmt.get("ext") not in {"mhtml", "html"}
    ]

    best_audio = max(
        audio_only,
        key=lambda fmt: fmt.get("abr") or fmt.get("tbr") or 0,
        default=None,
    )

    video_formats: list[dict[str, Any]] = []
    for fmt in formats:
        if fmt.get("vcodec") in (None, "none"):
            continue
        if not fmt.get("url"):
            continue
        if fmt.get("ext") in {"mhtml", "html"}:
            continue

        has_audio = fmt.get("acodec") not in (None, "none")
        height = fmt.get("height")
        size = fmt.get("filesize") or fmt.get("filesize_approx")
        video_formats.append({
            "format_id": fmt["format_id"],
            "format_type": "video",
            "file_type": fmt.get("ext"),
            "resolution": f"{height}p" if height else None,
            "height": height or 0,
            "fps": fmt.get("fps"),
            "video_codec": fmt.get("vcodec"),
            "audio_codec": (
                fmt.get("acodec") if has_audio
                else (best_audio.get("acodec") if best_audio else None)
            ),
            "no_audio": not has_audio,
            "tbr": fmt.get("tbr") or 0,
            "size_label": format_size(size),
            "filename": f"{title}.{fmt.get('ext')}",
        })

    video_formats.sort(key=lambda item: (item["height"], item["tbr"]), reverse=True)

    unique_video: dict[tuple, dict[str, Any]] = {}
    for item in video_formats:
        key = (item["resolution"], item["fps"], item["file_type"], item["no_audio"])
        current = unique_video.get(key)
        if current is None or item["tbr"] > current["tbr"]:
            unique_video[key] = item
    video_formats = list(unique_video.values())
    video_formats.sort(key=lambda item: (item["height"], item["tbr"]), reverse=True)

    audio_formats: list[dict[str, Any]] = []
    for fmt in audio_only:
        abr = fmt.get("abr") or fmt.get("tbr")
        size = fmt.get("filesize") or fmt.get("filesize_approx")
        audio_formats.append({
            "format_id": fmt["format_id"],
            "format_type": "audio",
            "file_type": fmt.get("ext"),
            "bitrate": round(abr) if abr else None,
            "audio_codec": fmt.get("acodec"),
            "size_label": format_size(size),
            "filename": f"{title}.{fmt.get('ext')}",
        })

    audio_formats.sort(key=lambda item: item["bitrate"] or 0, reverse=True)

    return {
        "title": title,
        "thumbnail": info.get("thumbnail"),
        "duration": info.get("duration"),
        "duration_label": format_duration(info.get("duration")),
        "uploader": info.get("uploader") or info.get("channel"),
        "video": video_formats,
        "audio": audio_formats,
        "has_separate_audio": best_audio is not None,
    }


def ydl_download_options(
    *,
    kind: str,
    format_id: str,
    outtmpl: str,
) -> dict[str, Any]:
    options: dict[str, Any] = {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "outtmpl": outtmpl,
        "restrictfilenames": True,
        "retries": 3,
        "impersonate": FIREFOX,
    }

    if kind == "merged":
        options["format"] = f"{format_id}+bestaudio/{format_id}"
        options["merge_output_format"] = "mp4"
        options["postprocessors"] = [
            {"key": "FFmpegVideoRemuxer", "preferedformat": "mp4"},
        ]
    elif kind == "video":
        options["format"] = format_id
    elif kind == "audio":
        options["format"] = format_id
    elif kind == "extract_audio":
        options["format"] = format_id
        options["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "m4a",
                "preferredquality": "192",
            },
        ]
    else:
        raise ValueError("Unknown download kind.")

    return options
