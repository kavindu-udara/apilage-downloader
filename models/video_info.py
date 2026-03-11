from typing import Optional
from urllib.parse import urlparse

class VideoInfo:
    def __init__(self, url: Optional[str] = None):
        self._url: Optional[str] = None
        if url:
            self.url = url  # Uses the setter with validation
    
    @property
    def url(self) -> Optional[str]:
        """Get the video URL."""
        return self._url
    
    @url.setter
    def url(self, value: str):
        """Set and validate the video URL."""
        if not value or not isinstance(value, str):
            raise ValueError("URL must be a non-empty string")
        
        value = value.strip()
        if not value:
            raise ValueError("URL cannot be empty or whitespace")
        
        # Basic URL validation
        parsed = urlparse(value)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError(f"Invalid URL format: {value}")
        
        self._url = value
    
    @property
    def is_valid(self) -> bool:
        """Check if URL is set and valid."""
        return self._url is not None
    
    @property
    def fetched_info(self) -> dict:
        """Get fetched video information."""
        return getattr(self, "_fetched_info", {})

    @fetched_info.setter
    def fetched_info(self, info: dict):
        """Set fetched video information."""
        self._fetched_info = info