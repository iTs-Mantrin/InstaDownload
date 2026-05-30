from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from services.youtube_service import YouTubeService
from utils.errors import DownloaderError
from utils.schemas import DownloadRequest, DownloadResponse, ErrorResponse, VideoInfoRequest, VideoInfoResponse


router = APIRouter()
service = YouTubeService()


@router.post(
    "/info",
    response_model=VideoInfoResponse,
    responses={400: {"model": ErrorResponse}, 403: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
async def get_video_info(payload: VideoInfoRequest) -> VideoInfoResponse:
    try:
        return await service.fetch_video_info(payload)
    except DownloaderError as error:
        raise HTTPException(status_code=error.status_code, detail=error.message) from error


@router.post(
    "/download",
    response_model=DownloadResponse,
    responses={400: {"model": ErrorResponse}, 403: {"model": ErrorResponse}, 404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def create_download(payload: DownloadRequest, request: Request) -> DownloadResponse:
    try:
        return await service.create_download(payload, str(request.base_url).rstrip("/"))
    except DownloaderError as error:
        raise HTTPException(status_code=error.status_code, detail=error.message) from error


@router.get("/downloads/{token}")
async def get_downloaded_file(token: str):
    try:
        resolved = service.resolve_download(token)
    except DownloaderError as error:
        raise HTTPException(status_code=error.status_code, detail=error.message) from error

    return FileResponse(
        path=resolved.file_path,
        filename=resolved.filename,
        media_type=resolved.media_type,
        background=BackgroundTask(service.cleanup_download, resolved.directory),
    )
