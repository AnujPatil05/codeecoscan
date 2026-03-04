"""Custom exception hierarchy for CodeEcoScan.

All service-specific exceptions inherit from ``CodeEcoScanError`` so that
exception handlers in the FastAPI layer can catch broad or narrow categories.
"""


class CodeEcoScanError(Exception):
    """Base exception for all CodeEcoScan errors."""

    def __init__(self, message: str = "An unexpected error occurred.") -> None:
        self.message = message
        super().__init__(self.message)


class CodeParsingError(CodeEcoScanError):
    """Raised when ``ast.parse`` encounters a syntax error in user code.

    This maps to HTTP 400 — the client submitted unparseable code.
    """

    def __init__(self, message: str = "The provided code contains syntax errors.") -> None:
        super().__init__(message)


class AnalysisError(CodeEcoScanError):
    """Raised when an unexpected failure occurs during AST traversal.

    This maps to HTTP 500 — the system failed, not the user input.
    """

    def __init__(self, message: str = "An error occurred during code analysis.") -> None:
        super().__init__(message)
