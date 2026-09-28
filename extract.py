import json
from typing import Any

import yt_dlp  # pyright: ignore[reportMissingModuleSource]


def get_formats(url: str) -> dict[str, Any]:
    options = {
        "quiet": True,
        "no_warnings": True,
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=False)

    video_formats = []
    audio_formats = []

    formats = info.get("formats", [])

    audio_only = [
        fmt
        for fmt in formats
        if fmt.get("vcodec") == "none"
        and fmt.get("acodec") != "none"
        and fmt.get("url")
    ]

    # Highest bitrate audio as the default audio to pair with video-only formats.
    best_audio = max(
        audio_only,
        key=lambda fmt: fmt.get("abr") or 0,
        default=None,
    )

    for fmt in formats:
        if fmt.get("vcodec") == "none":
            continue

        if not fmt.get("url"):
            continue

        has_audio = fmt.get("acodec") != "none"

        # Format already contains both video and audio.
        if has_audio:
            video_formats.append({
                "format_id": fmt["format_id"],
                "format_type": "video",
                "file_type": fmt.get("ext"),
                "resolution": (
                    f'{fmt["height"]}p'
                    if fmt.get("height")
                    else None
                ),
                "fps": fmt.get("fps"),
                "video_codec": fmt.get("vcodec"),
                "audio_codec": fmt.get("acodec"),
                "no_audio": False,
                "video_url": fmt["url"],
                "audio_url": None,
                "filename": f'{info["title"]}.{fmt.get("ext")}',
            })

        # Video-only format.
        else:
            video_formats.append({
                "format_id": fmt["format_id"],
                "format_type": "video",
                "file_type": fmt.get("ext"),
                "resolution": (
                    f'{fmt["height"]}p'
                    if fmt.get("height")
                    else None
                ),
                "fps": fmt.get("fps"),
                "video_codec": fmt.get("vcodec"),
                "audio_codec": best_audio.get("acodec")
                if best_audio
                else None,
                "no_audio": best_audio is None,
                "video_url": fmt["url"],
                "audio_url": best_audio.get("url")
                if best_audio
                else None,
                "filename": f'{info["title"]}.{fmt.get("ext")}',
            })

    # Audio-only formats
    for fmt in audio_only:
        abr = fmt.get("abr")

        audio_formats.append({
            "format_id": fmt["format_id"],
            "format_type": "audio",
            "file_type": fmt.get("ext"),
            "bitrate": round(abr) if abr else None,
            "audio_codec": fmt.get("acodec"),
            "filename": f'{info["title"]}.{fmt.get("ext")}',
            "url": fmt["url"],
        })

    return {
        "title": info.get("title"),
        "thumbnail": info.get("thumbnail"),
        "duration": info.get("duration"),
        "video": video_formats,
        "audio": audio_formats,
    }

url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

result = get_formats(url)

with open("formats.json", "w", encoding="utf-8") as file:
    json.dump(result, file, indent=2, ensure_ascii=False)