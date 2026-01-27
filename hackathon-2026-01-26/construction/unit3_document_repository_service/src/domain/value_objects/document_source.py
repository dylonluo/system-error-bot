"""DocumentSource value object."""

from enum import Enum


class Source(str, Enum):
    """Document source enumeration."""

    S3 = "s3"
    CONFLUENCE = "confluence"


class DocumentSource:
    """Document source with platform identifier."""

    def __init__(self, value: Source, platform_id: str):
        if not isinstance(value, Source):
            raise ValueError(f"Invalid document source: {value}")
        if not platform_id or len(platform_id.strip()) == 0:
            raise ValueError("Platform ID cannot be empty")

        self._value = value
        self._platform_id = platform_id.strip()

    @property
    def value(self) -> Source:
        return self._value

    @property
    def platform_id(self) -> str:
        return self._platform_id

    def is_s3(self) -> bool:
        return self._value == Source.S3

    def is_confluence(self) -> bool:
        return self._value == Source.CONFLUENCE

    def get_platform_id(self) -> str:
        return self._platform_id

    def __eq__(self, other) -> bool:
        if not isinstance(other, DocumentSource):
            return False
        return self._value == other._value and self._platform_id == other._platform_id

    def __hash__(self) -> int:
        return hash((self._value, self._platform_id))

    def __str__(self) -> str:
        return f"{self._value.value}:{self._platform_id}"

    def __repr__(self) -> str:
        return f"DocumentSource({self._value.value}, {self._platform_id})"
