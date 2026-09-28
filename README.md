# CyTube

A small, local download portal for people who can run Python and just want the
file — without a website full of ads, premium walls, or a slow “wait 30 seconds”
UI.

Paste a **public** YouTube, Instagram, Facebook, TikTok, Dailymotion, or
Bilibili URL, list formats, and download video+audio, video only, or audio
only. It runs on your machine. There is no account, no cookie login, and no
hosted “free downloader” business in this repo.

## Why this exists

The web is full of download sites. Many of them work until they don’t: popups,
forced waits, “premium to unlock 1080p,” and interfaces that exist to extract
clicks instead of files.

This project is for **power users** who already have a terminal, want
**absolute control** over what happens on their own computer, and would rather
run a few commands than fight someone else’s ad funnel.

It is personal tooling. It is not a product pitch for a public download mill.

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- **FFmpeg + ffprobe on your system `PATH`** — not optional if you want
  real quality. `uv sync` will not install them. See [FFmpeg](#ffmpeg) below.

## Quick start

```bash
git clone https://github.com/ishantoz/cytube.git
cd cytube
uv sync
```

Desktop (starts the local server and opens a window):

```bash
uv run cytube
```

The same UI is also a normal website on your machine:

```text
http://127.0.0.1:8000
```

Browser-only (no window):

```bash
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Public links only. Private, login-walled, or DRM-protected media is out of
scope.

## FFmpeg

**You must install FFmpeg on Windows, macOS, or Linux yourself.** CyTube does
not ship it. `uv sync` only installs Python packages.

[yt-dlp](https://github.com/yt-dlp/yt-dlp) is a Python library. It talks to
sites and downloads streams. **FFmpeg is a separate native program** (`ffmpeg`
and `ffprobe`). This app calls yt-dlp; yt-dlp calls FFmpeg when a download is
not a single finished file.

### Why it actually matters here

Sites like YouTube often serve **video and audio as two streams**. The UI’s
**Video + audio** button asks yt-dlp to fetch both and **merge** them into one
mp4. That merge is FFmpeg. **Extract audio** from a video file is also FFmpeg.

Without FFmpeg:

| Action in this app | What usually happens |
| --- | --- |
| Fetch formats | Works |
| Video only / audio only (already one file) | Often works |
| **Video + audio** | Cannot merge. yt-dlp typically falls back to a **pre-muxed, lower-quality** file (often ~360p on YouTube) or the job fails |
| **Extract audio** | Fails or skips post-processing |

If you skip FFmpeg, CyTube still “runs.” You just do not get the downloads the
UI is built around.

### Why this is not `uv add ffmpeg`

- FFmpeg is a **C binary**, not a Python module.
- yt-dlp **on purpose** does not vendor FFmpeg; that would make every install
  tens of megabytes larger for people who only list formats.
- Pip/uv packages that wrap FFmpeg either ship a **huge wheel**, download
  binaries on **first run** (not during `uv sync`), or omit `ffprobe`. yt-dlp
  wants **both** `ffmpeg` and `ffprobe` on `PATH`.
- A **system install** is the normal, supported path: one copy for this app,
  the terminal, and everything else.

### Pros of installing it on the system

- Merges and audio extract work the way the UI says
- `ffprobe` is there next to `ffmpeg` (don’t copy a lone `ffmpeg.exe`)
- You control the build (Homebrew, apt, winget, or [yt-dlp’s FFmpeg builds](https://github.com/yt-dlp/FFmpeg-Builds))
- One install; upgrades are yours

### Cons / costs

- Extra step after `uv sync` — easy to forget, then “Video + audio” looks broken
- You have to use a **package manager or zip** for your OS; it is not in this repo
- FFmpeg’s own license (often **GPL** for full builds) is separate from this
  project and from yt-dlp
- `PATH` must be visible to the same terminal (or desktop app) that runs CyTube.
  A PATH change in another window does not count
- You are responsible for getting a build that matches your CPU (Intel vs Apple
  Silicon, x64 vs ARM)

### Install

Confirm nothing is found yet:

```bash
ffmpeg -version
ffprobe -version
```

**macOS** (Homebrew):

```bash
brew install ffmpeg
```

**Windows** (winget, in an admin or user prompt):

```powershell
winget install Gyan.FFmpeg
```

Or [Scoop](https://scoop.sh/): `scoop install ffmpeg`. Or download a static
build, put `ffmpeg.exe` and `ffprobe.exe` in the same folder, add that folder
to **User PATH**, then **open a new** terminal.

**Linux** (Debian / Ubuntu):

```bash
sudo apt update
sudo apt install ffmpeg
```

Fedora: `sudo dnf install ffmpeg`. Arch: `sudo pacman -S ffmpeg`.

Close and reopen the terminal (and CyTube) after installing. If `ffmpeg
-version` works in that shell, this app can see it too.

## What it does

- Lists formats with [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- Downloads in a temp folder, streams the file to you, then deletes the server copy
- Runs several downloads at once; cancel is confirm-then-stop
- JSON API under `/api` if you want to drive it yourself

## Third-party libraries and licenses

This app is a thin UI around other people’s work. **Each dependency keeps its
own license.** You must follow those licenses as well as the terms of the sites
you download from. Read the license file in each project (or on PyPI) before
you redistribute CyTube or ship a binary.

| Package | Used for | License (upstream) |
| --- | --- | --- |
| [yt-dlp](https://github.com/yt-dlp/yt-dlp) | Extract URLs and download media | Unlicense |
| FFmpeg (`ffmpeg` / `ffprobe`) | **System install** — merge, remux, extract audio | [FFmpeg licensing](https://ffmpeg.org/legal.html) (build-dependent, often GPL) |
| [curl-cffi](https://github.com/lexiforest/curl_cffi) | TLS impersonation some extractors need | MIT |
| [FastAPI](https://github.com/fastapi/fastapi) | HTTP app | MIT |
| [Uvicorn](https://github.com/Kludex/uvicorn) | ASGI server | BSD-3-Clause |
| [Jinja2](https://github.com/pallets/jinja) | HTML templates | BSD-3-Clause |
| [python-multipart](https://github.com/Kludex/python-multipart) | Form bodies | Apache-2.0 |
| [pywebview](https://github.com/r0x0r/pywebview) | Desktop window | BSD-3-Clause |

The page also loads **Tailwind CSS** and **Flowbite** from a CDN. Those
projects have their own licenses and terms.

Versions are pinned in `pyproject.toml` and `uv.lock`. Do not copy this table
as legal advice; the upstream repo is the source of truth.

## Caution: copyright and how you must not use this

Downloading someone else’s video, audio, or other content can violate
**copyright** and the **terms of the platform**. “I ran an open-source tool”
does not make an unauthorized copy legal.

Use this **only** for material you have the right to copy: your own uploads,
content under a license that allows download, or other cases where the law in
your country actually allows it. When you are unsure, don’t download it.

**Do not:**

- Use this as a pirate stash or a way to skip paying for media
- Run it as a **public website**, SaaS, or “free downloader” index so strangers
  can fetch copyrighted files
- Charge money, run ads, or otherwise **make income** by hosting this for
  other people
- Point it at private / login-walled posts or try to break DRM

If you put this on the internet as a business, you are not using the project
as intended, and you take on the legal risk yourself. The maintainers are not
offering a commercial download service and are not responsible for how you
use the code.

This is **personal, local use** for people who already know what they are
doing. Keep it that way.

## Agent / contributor notes

AI and humans working in this repo should start at `AGENTS.md`. Workflow docs
live under `blueprint/`.
