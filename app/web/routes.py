from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.logic.extractor import PLATFORMS

WEB_ROOT = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(WEB_ROOT / "templates"))

router = APIRouter()


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


@router.api_route("/", methods=["GET", "HEAD"], include_in_schema=False)
def home() -> RedirectResponse:
    return RedirectResponse("/youtube", status_code=307)


@router.get("/{platform}", response_class=HTMLResponse)
def platform_page(request: Request, platform: str) -> HTMLResponse:
    if platform not in PLATFORMS:
        return render(
            request,
            "partials/error.html",
            {"message": "Unknown platform."},
            status_code=404,
        )
    return render(request, "platform.html", platform_context(request, platform))
