from dataclasses import dataclass
from typing import Any, List, Dict, Union


@dataclass(frozen=True)
class MetricValue:
    """Value object representing a metric value with unit."""
    
    value: Union[int, float, List, Dict]
    unit: str  # count, percentage, list, etc.
    
    def __post_init__(self):
        if self.value is None:
            raise ValueError("Metric value cannot be None")
        if not self.unit:
            raise ValueError("Metric unit cannot be empty")
    
    def as_integer(self) -> int:
        """Get value as integer."""
        if isinstance(self.value, int):
            return self.value
        if isinstance(self.value, float):
            return int(self.value)
        raise ValueError(f"Cannot convert {type(self.value)} to integer")
    
    def as_float(self) -> float:
        """Get value as float."""
        if isinstance(self.value, (int, float)):
            return float(self.value)
        raise ValueError(f"Cannot convert {type(self.value)} to float")
    
    def as_list(self) -> List:
        """Get value as list."""
        if isinstance(self.value, list):
            return self.value
        raise ValueError(f"Value is not a list: {type(self.value)}")
    
    def as_dict(self) -> Dict:
        """Get value as dictionary."""
        if isinstance(self.value, dict):
            return self.value
        raise ValueError(f"Value is not a dictionary: {type(self.value)}")
    
    def __str__(self):
        if isinstance(self.value, (int, float)):
            return f"{self.value} {self.unit}"
        return f"{self.value}"
