"""DocumentType value object."""

from enum import Enum


class DocType(str, Enum):
    """Document type enumeration."""

    SOP = "sop"
    PRD = "prd"
    GUIDE = "guide"
    OTHER = "other"


class DocumentType:
    """Document type classification."""

    def __init__(self, value: DocType):
        if not isinstance(value, DocType):
            raise ValueError(f"Invalid document type: {value}")
        self._value = value

    @property
    def value(self) -> DocType:
        return self._value

    def is_sop(self) -> bool:
        return self._value == DocType.SOP

    def is_prd(self) -> bool:
        return self._value == DocType.PRD

    def is_guide(self) -> bool:
        return self._value == DocType.GUIDE

    def __eq__(self, other) -> bool:
        if not isinstance(other, DocumentType):
            return False
        return self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)

    def __str__(self) -> str:
        return self._value.value

    def __repr__(self) -> str:
        return f"DocumentType({self._value.value})"
