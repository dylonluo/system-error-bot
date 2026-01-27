"""Screenshot validation domain service"""
import re
from dataclasses import dataclass
from ..value_objects.screenshot import Screenshot


@dataclass
class ValidationResult:
    """Result of screenshot validation"""
    is_valid: bool
    error_message: str = None


class ScreenshotValidationService:
    """Domain service for validating screenshots"""

    def validate_screenshot(self, screenshot: Screenshot) -> ValidationResult:
        """Validate a screenshot"""
        # Check format
        if not screenshot.is_valid_format():
            return ValidationResult(
                is_valid=False,
                error_message=f"Invalid format: {screenshot.mime_type}. Only JPEG and PNG allowed."
            )

        # Check size
        if not screenshot.is_within_size_limit():
            return ValidationResult(
                is_valid=False,
                error_message=f"File size {screenshot.size} exceeds limit of {Screenshot.MAX_SIZE} bytes"
            )

        return ValidationResult(is_valid=True)

    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to prevent security issues"""
        # Remove path separators
        filename = filename.replace('/', '_').replace('\\', '_')

        # Remove special characters except dots, dashes, underscores
        filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)

        # Limit length
        if len(filename) > 255:
            name_parts = filename.rsplit('.', 1)
            if len(name_parts) == 2:
                name, ext = name_parts
                filename = name[:250] + '.' + ext
            else:
                filename = filename[:255]

        return filename
