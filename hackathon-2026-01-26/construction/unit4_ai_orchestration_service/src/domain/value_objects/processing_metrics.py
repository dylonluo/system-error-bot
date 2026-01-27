from dataclasses import dataclass


@dataclass(frozen=True)
class ProcessingMetrics:
    """Performance metrics for query processing."""
    total_time_ms: int
    ai_processing_time_ms: int
    document_search_time_ms: int
    filtering_time_ms: int
    tokens_used: int
    cost_usd: float

    @classmethod
    def create(
        cls,
        total_time_ms: int = 0,
        ai_processing_time_ms: int = 0,
        document_search_time_ms: int = 0,
        filtering_time_ms: int = 0,
        tokens_used: int = 0,
        cost_usd: float = 0.0,
    ) -> "ProcessingMetrics":
        return cls(
            total_time_ms=total_time_ms,
            ai_processing_time_ms=ai_processing_time_ms,
            document_search_time_ms=document_search_time_ms,
            filtering_time_ms=filtering_time_ms,
            tokens_used=tokens_used,
            cost_usd=cost_usd,
        )
