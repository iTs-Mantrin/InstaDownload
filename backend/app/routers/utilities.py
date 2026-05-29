"""Utility tools API routes."""

import os
import io
import qrcode
import hashlib
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel

from app.utils.helpers import clean_old_files
from app.config import get_settings

router = APIRouter(prefix="/api/utils", tags=["Utilities"])
settings = get_settings()


# ── YouTube Thumbnail Downloader ──────────────────────────────

@router.get("/thumbnail")
def get_thumbnail(url: str = Query(..., description="YouTube video URL")):
    """Download the thumbnail of a YouTube video."""
    import yt_dlp
    from urllib.parse import parse_qs, urlparse

    # Extract video ID
    video_id = None
    parsed = urlparse(url)
    if "youtu.be" in parsed.netloc:
        video_id = parsed.path.strip("/")
    elif "youtube.com" in parsed.netloc:
        qs = parse_qs(parsed.query)
        video_id = qs.get("v", [None])[0]

    if not video_id:
        # Try yt-dlp fallback
        try:
            with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True}) as ydl:
                info = ydl.extract_info(url, download=False)
                video_id = info.get("id")
        except Exception:
            pass

    if not video_id:
        raise HTTPException(400, "Could not extract video ID")

    # Try multiple thumbnail resolutions
    for resolution in ["maxresdefault", "sddefault", "hqdefault", "default"]:
        thumb_url = f"https://img.youtube.com/vi/{video_id}/{resolution}.jpg"
        import requests
        try:
            r = requests.get(thumb_url, timeout=10)
            if r.status_code == 200 and len(r.content) > 1000:
                return Response(
                    content=r.content,
                    media_type="image/jpeg",
                    headers={
                        "Content-Disposition": f'attachment; filename="{video_id}_{resolution}.jpg"'
                    },
                )
        except Exception:
            continue

    raise HTTPException(404, "Thumbnail not found")


# ── QR Code Generator ─────────────────────────────────────────

class QRRequest(BaseModel):
    data: str
    size: int = 300


@router.post("/qrcode")
def generate_qr(req: QRRequest):
    """Generate a QR code image."""
    if not req.data or len(req.data) > 2000:
        raise HTTPException(400, "Invalid data (max 2000 chars)")
    try:
        qr = qrcode.QRCode(box_size=10, border=2)
        qr.add_data(req.data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return Response(
            content=buf.getvalue(),
            media_type="image/png",
            headers={"Content-Disposition": 'attachment; filename="qrcode.png"'},
        )
    except Exception as e:
        raise HTTPException(500, f"QR generation failed: {e}")


# ── Hashtag Generator ─────────────────────────────────────────

class HashtagRequest(BaseModel):
    keywords: list[str]
    count: int = 10


HASHTAG_SUGGESTIONS = {
    "travel": ["travel", "wanderlust", "adventure", "explore", "vacation",
               "travelgram", "trip", "holiday", "nature", "journey"],
    "food": ["food", "foodie", "instafood", "delicious", "yummy",
             "foodporn", "homemade", "tasty", "cooking", "eat"],
    "fitness": ["fitness", "workout", "gym", "motivation", "health",
                "training", "fit", "bodybuilding", "exercise", "wellness"],
    "fashion": ["fashion", "style", "outfit", "ootd", "trendy",
                "vintage", "streetwear", "look", "couture", "styleblogger"],
    "music": ["music", "song", "artist", "singer", "band",
              "album", "concert", "melody", "lyrics", "musician"],
}


@router.post("/hashtags")
def generate_hashtags(req: HashtagRequest):
    """Generate relevant hashtags from keywords."""
    if not req.keywords:
        raise HTTPException(400, "At least one keyword required")

    tags = set()
    for kw in req.keywords:
        kw_lower = kw.lower().strip()
        tags.add(f"#{kw_lower}")
        # Add category-based suggestions
        for category, suggestions in HASHTAG_SUGGESTIONS.items():
            if any(word in kw_lower for word in category.split()):
                for s in suggestions[:req.count]:
                    tags.add(f"#{s}")
        # Add keyword variations
        tags.add(f"#{kw_lower}love")
        tags.add(f"#{kw_lower}oftheday")

    # Ensure minimum count
    result = list(tags)
    while len(result) < min(req.count, 5):
        result.append(f"#instadaily")
    return {"hashtags": result[:req.count]}


# ── Image Compressor (Server-side placeholder) ────────────────

@router.post("/compress")
async def compress_image(file: bytes):
    """Simple image compression (re-encode as JPEG with quality=85)."""
    try:
        from PIL import Image
        import io as _io
        img = Image.open(_io.BytesIO(file))
        output = _io.BytesIO()
        # Convert to RGB if needed (for RGBA -> JPEG)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img.save(output, format="JPEG", quality=85, optimize=True)
        output.seek(0)
        return Response(
            content=output.getvalue(),
            media_type="image/jpeg",
            headers={"Content-Disposition": 'attachment; filename="compressed.jpg"'},
        )
    except Exception as e:
        raise HTTPException(400, f"Compression failed: {e}")
