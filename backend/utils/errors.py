class DownloaderError(Exception):
    def __init__(self, status_code: int, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.message = message

    @classmethod
    def bad_request(cls, message: str) -> "DownloaderError":
        return cls(400, message)

    @classmethod
    def forbidden(cls, message: str) -> "DownloaderError":
        return cls(403, message)

    @classmethod
    def not_found(cls, message: str) -> "DownloaderError":
        return cls(404, message)

    @classmethod
    def download_failed(cls, message: str) -> "DownloaderError":
        return cls(500, message)
