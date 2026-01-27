"""In-memory screenshot storage implementation"""
import base64
from typing import Dict, Optional
from uuid import uuid4


class InMemoryScreenshotStorage:
    """In-memory storage for screenshots"""

    def __init__(self):
        self._storage: Dict[str, str] = {}  # url -> base64 content

    def store(self, content: bytes, filename: str, mime_type: str) -> str:
        """Store screenshot and return URL"""
        # Generate unique URL
        file_id = str(uuid4())
        url = f"memory://screenshots/{file_id}/{filename}"

        # Store as base64
        base64_content = base64.b64encode(content).decode('utf-8')
        self._storage[url] = base64_content

        return url

    def retrieve(self, url: str) -> Optional[bytes]:
        """Retrieve screenshot by URL"""
        base64_content = self._storage.get(url)
        if base64_content is None:
            return None

        return base64.b64decode(base64_content)

    def delete(self, url: str) -> None:
        """Delete screenshot"""
        if url in self._storage:
            del self._storage[url]

    def exists(self, url: str) -> bool:
        """Check if screenshot exists"""
        return url in self._storage

    def clear(self) -> None:
        """Clear all screenshots (for testing)"""
        self._storage.clear()
