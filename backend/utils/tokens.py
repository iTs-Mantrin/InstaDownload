from pathlib import Path

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from utils.config import get_settings
from utils.errors import DownloaderError


def _serializer() -> URLSafeTimedSerializer:
    settings = get_settings()
    return URLSafeTimedSerializer(settings.download_token_secret, salt="download-token")


def create_download_token(directory: Path, filename: str) -> str:
    payload = {"directory": directory.name, "filename": filename}
    return _serializer().dumps(payload)


def read_download_token(token: str) -> tuple[str, str]:
    settings = get_settings()

    try:
        payload = _serializer().loads(token, max_age=settings.download_token_ttl_seconds)
    except SignatureExpired as error:
        raise DownloaderError.not_found("The download link has expired.") from error
    except BadSignature as error:
        raise DownloaderError.bad_request("The download link is invalid.") from error

    directory = payload.get("directory")
    filename = payload.get("filename")

    if not isinstance(directory, str) or not isinstance(filename, str):
        raise DownloaderError.bad_request("The download link is invalid.")

    return directory, filename
