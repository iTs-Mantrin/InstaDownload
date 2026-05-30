import asyncio
import mimetypes
from pathlib import Path
from typing import Any

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

from utils.config import get_settings
from utils.errors import DownloaderError
from utils.schemas import DownloadRequest, DownloadResponse, DownloadedFile, FormatOption, VideoInfoRequest, VideoInfoResponse
from utils.temp_files import create_download_directory, find_downloaded_file, remove_directory, remove_expired_temp_directories
from utils.tokens import create_download_token, read_download_token
from utils.validators import normalize_audio_quality, normalize_video_quality, validate_youtube_url


class YouTubeService:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def fetch_video_info(self, payload: VideoInfoRequest) -> VideoInfoResponse:
        validated_url = validate_youtube_url(payload.url)
        remove_expired_temp_directories(self.settings.temp_dir, self.settings.download_token_ttl_seconds)

        info = await asyncio.to_thread(self._extract_info, validated_url)
        formats = self._build_format_options(info)

        return VideoInfoResponse(
            title=info.get("title") or "Unknown title",
            thumbnail=info.get("thumbnail"),
            duration=int(info.get("duration") or 0),
            formats=formats,
        )

    async def create_download(self, payload: DownloadRequest, base_url: str) -> DownloadResponse:
        validated_url = validate_youtube_url(payload.url)
        remove_expired_temp_directories(self.settings.temp_dir, self.settings.download_token_ttl_seconds)

        download_directory = create_download_directory(self.settings.temp_dir)

        try:
            filename = await asyncio.to_thread(self._download_media, validated_url, payload, download_directory)
        except Exception:
            remove_directory(download_directory)
            raise

        token = create_download_token(download_directory, filename)
        media_url = f"{base_url}/api/downloads/{token}"
        extension = Path(filename).suffix.lstrip(".")

        return DownloadResponse(
            download_url=media_url,
            filename=filename,
            format=payload.format,
            quality=payload.quality,
            expires_in=self.settings.download_token_ttl_seconds,
            extension=extension,
        )

    def resolve_download(self, token: str) -> DownloadedFile:
        remove_expired_temp_directories(self.settings.temp_dir, self.settings.download_token_ttl_seconds)
        directory_name, filename = read_download_token(token)

        directory = (self.settings.temp_dir / directory_name).resolve()
        file_path = (directory / filename).resolve()

        if self.settings.temp_dir.resolve() not in file_path.parents:
            raise DownloaderError.bad_request("Invalid download token.")

        if not file_path.exists() or not file_path.is_file():
            raise DownloaderError.not_found("The download has expired or is no longer available.")

        media_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"

        return DownloadedFile(
            file_path=file_path,
            filename=file_path.name,
            media_type=media_type,
            directory=directory,
        )

    def cleanup_download(self, directory: Path) -> None:
        remove_directory(directory)

    def _extract_info(self, url: str) -> dict[str, Any]:
        options = {
            "quiet": True,
            "skip_download": True,
            "no_warnings": True,
            "noplaylist": True,
            "cookiefile": self.settings.yt_dlp_cookies_file,
        }

        try:
            with YoutubeDL(options) as downloader:
                return downloader.extract_info(url, download=False)
        except DownloadError as error:
            raise self._map_download_error(error) from error

    def _download_media(self, url: str, payload: DownloadRequest, directory: Path) -> str:
        output_template = str(directory / "%(title).120B-%(id)s.%(ext)s")
        options: dict[str, Any] = {
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "outtmpl": output_template,
            "cookiefile": self.settings.yt_dlp_cookies_file,
        }

        if payload.format == "mp3":
            preferred_quality = normalize_audio_quality(payload.quality)
            options.update(
                {
                    "format": "bestaudio/best",
                    "postprocessors": [
                        {
                            "key": "FFmpegExtractAudio",
                            "preferredcodec": "mp3",
                            "preferredquality": preferred_quality,
                        }
                    ],
                    "final_ext": "mp3",
                }
            )
            expected_extension = ".mp3"
        else:
            preferred_quality = normalize_video_quality(payload.quality)
            options.update(
                {
                    "format": self._build_video_selector(preferred_quality),
                    "merge_output_format": "mp4",
                    "final_ext": "mp4",
                }
            )
            expected_extension = ".mp4"

        try:
            with YoutubeDL(options) as downloader:
                downloader.download([url])
        except DownloadError as error:
            raise self._map_download_error(error) from error
        except Exception as error:
            raise DownloaderError.download_failed(f"Download failed: {error}") from error

        file_path = find_downloaded_file(directory, expected_extension)
        if file_path is None:
            raise DownloaderError.download_failed("Download finished but the output file could not be found.")

        return file_path.name

    def _build_video_selector(self, quality: str) -> str:
        if quality == "highest":
            return "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"

        return f"bestvideo[ext=mp4][height<={quality}]+bestaudio[ext=m4a]/best[ext=mp4][height<={quality}]/best[height<={quality}]"

    def _build_format_options(self, info: dict[str, Any]) -> list[FormatOption]:
        seen_video_qualities: set[str] = set()
        formats: list[FormatOption] = []

        raw_formats = info.get("formats") or []
        mp4_formats = sorted(
            (
                item
                for item in raw_formats
                if item.get("vcodec") not in (None, "none") and item.get("height") and item.get("ext") == "mp4"
            ),
            key=lambda item: int(item.get("height") or 0),
            reverse=True,
        )

        for item in mp4_formats:
            quality = str(int(item["height"]))
            if quality in seen_video_qualities:
                continue
            seen_video_qualities.add(quality)

            formats.append(
                FormatOption(
                    format="mp4",
                    quality=quality,
                    label=f"{quality}p MP4",
                    extension="mp4",
                    filesize=item.get("filesize") or item.get("filesize_approx"),
                )
            )

        formats.insert(
            0,
            FormatOption(
                format="mp4",
                quality="highest",
                label="Best quality MP4",
                extension="mp4",
                filesize=None,
            ),
        )

        for bitrate in ("128", "192", "320"):
            formats.append(
                FormatOption(
                    format="mp3",
                    quality=bitrate,
                    label=f"{bitrate} kbps MP3",
                    extension="mp3",
                    filesize=None,
                )
            )

        return formats

    def _map_download_error(self, error: DownloadError) -> DownloaderError:
        message = str(error).strip() or "yt-dlp failed to process this video."
        lowered = message.lower()

        if "private video" in lowered or "video is private" in lowered:
            return DownloaderError.forbidden("This video is private and cannot be downloaded.")
        if "sign in to confirm your age" in lowered or "age-restricted" in lowered:
            return DownloaderError.forbidden("This video is age-restricted and requires authentication.")
        if "unsupported url" in lowered or "invalid url" in lowered:
            return DownloaderError.bad_request("The provided URL is invalid.")
        if "video unavailable" in lowered or "not available" in lowered:
            return DownloaderError.not_found("The requested video is unavailable.")

        return DownloaderError.download_failed(message)
