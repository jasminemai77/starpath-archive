"""Explicit errors for local runtime image-resource preparation."""

from __future__ import annotations


class RuntimeDeliveryError(ValueError):
    """Base error for safe runtime resource preparation."""


class RuntimeResourceNotFoundError(RuntimeDeliveryError):
    """Raised when a valid resource reference has no runtime file."""


class RuntimeResourceAccessError(RuntimeDeliveryError):
    """Raised when the runtime cannot safely inspect its configured asset root."""


class InvalidRuntimeResourceError(RuntimeDeliveryError):
    """Raised when a resource reference or resolved target violates runtime rules."""


class RuntimePayloadPreparationError(RuntimeDeliveryError):
    """Raised when an AstrBot payload cannot enter the runtime preparation boundary."""
