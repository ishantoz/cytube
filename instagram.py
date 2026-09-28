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
        "https://www.instagram.com/reel/DaAgT5_Qu-X/",
        "https://www.instagram.com/reels/DdtVfT9yxRT/",
        "https://www.instagram.com/reel/DdtV4p4SoCb/",
        "https://www.instagram.com/reel/DdtWLFQSQbZ/",
    ]

    with yt_dlp.YoutubeDL(options) as ydl:
        ydl.download(urls)


if __name__ == "__main__":
    main()