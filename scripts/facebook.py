import yt_dlp


options = {
    "outtmpl": "downloads/%(uploader)s_%(id)s.%(ext)s",

    "format": "bestvideo*+bestaudio/best",

    "merge_output_format": "mp4",

    "postprocessors": [
        {
            "key": "FFmpegVideoRemuxer",
            "preferedformat": "mp4",
        }
    ],

    "ignoreerrors": True,
}


def main() -> None:
    urls = [
        # TODO: Add URLs here
        # Example: "https://www.facebook.com/..."
        # Example: "https://www.facebook.com/..."
        # Example: "https://www.facebook.com/..."
    ]

    with yt_dlp.YoutubeDL(options) as ydl:
        ydl.download(urls)


if __name__ == "__main__":
    main()