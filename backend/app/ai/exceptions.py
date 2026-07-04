"""Custom exceptions for the PharmaChain AI reasoning pipeline."""


class AIException(Exception):
    """Base exception for AI-layer failures in the PharmaChain copilot."""


class PlanningException(AIException):
    """Raised when the planning layer cannot build an execution plan."""


class ToolExecutionException(AIException):
    """Raised when a registered AI tool fails during reasoning execution."""


class ResponseCompositionException(AIException):
    """Raised when structured evidence cannot be composed into a response."""
