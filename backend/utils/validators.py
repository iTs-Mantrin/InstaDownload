from urllib.parse import urlparse

from utils.errors import DownloaderError


ALLOWED_HOSTS = {
    "youtube.com",
    "www.youtube.com",
    "m.youtube.com",
    "music.youtube.com",
    "youtu.be",
}

ALLOWED_AUDIO_QUALITIES = {"128", "192", "320"}


def validate_youtube_url(url: str) -> str:
    normalized = url.strip()
    parsed = urlparse(normalized)

    if parsed.scheme not in {"http", "https"} or parsed.netloc.lower() not in ALLOWED_HOSTS:
        raise DownloaderError.bad_request("Please provide a valid YouTube URL.")

    return normalized


def normalize_audio_quality(quality: str) -> str:
    normalized = quality.strip()
    if normalized not in ALLOWED_AUDIO_QUALITIES:
        raise DownloaderError.bad_request("MP3 quality must be one of 128, 192, or 320.")
    return normalized


def normalize_video_quality(quality: str) -> str:
    normalized = quality.strip().lower().replace("p", "")
    if normalized == "highest":
        return normalized

    if not normalized.isdigit():
        raise DownloaderError.bad_request("MP4 quality must be a resolution like 360, 720, or 'highest'.")

    return normalized
