import yt_dlp


options = {
    "outtmpl": "downloads/instagram/%(uploader)s_%(id)s.%(ext)s",

    "format": "bestvideo*+bestaudio/best",

    "merge_output_format": "mp4",

    # Don't use cookies
    # "cookiesfrombrowser": ("chrome",),

    "postprocessors": [
        {
            "key": "FFmpegVideoRemuxer",
            "preferedformat": "mp4",
        }
    ],

    # Continue downloading other URLs if one fails
    "ignoreerrors": True,
}


def main() -> None:
    urls = [
        # TODO: Add URLs here
        # Example: "https://www.instagram.com/..."
        # Example: "https://www.instagram.com/..."
        # Example: "https://www.instagram.com/..."
        # Example: "https://www.instagram.com/..."
        # Example: "https://www.instagram.com/..."
    ]

    with yt_dlp.YoutubeDL(options) as ydl:
        ydl.download(urls)


if __name__ == "__main__":
    main()