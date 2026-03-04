"""Feature extraction orchestrator.

This module sits between the raw AST analyzer and the API layer.
It owns the responsibility of:

1. Sanitizing input code.
2. Creating a fresh ``CodeStructureAnalyzer`` per call (thread safety).
3. Mapping the raw ``AnalysisResult`` dataclass to the Pydantic
   ``ExtractedFeatures`` schema.
4. Translating low-level exceptions into service-level exceptions.
"""

from __future__ import annotations

from app.analysis.ast_analyzer import CodeStructureAnalyzer
from app.core.config import Settings
from app.core.exceptions import AnalysisError, CodeParsingError
from app.models.schemas import ExtractedFeatures
from app.utils.helpers import sanitize_code_input


MAX_CODE_LENGTH: int = 200_000
"""Maximum allowed input code length in characters.

Inputs exceeding this limit are rejected with a ``CodeParsingError``
(HTTP 400) to prevent excessive memory and CPU usage during AST parsing.
"""


class FeatureExtractor:
    """Orchestrates code analysis and feature extraction.

    A new ``CodeStructureAnalyzer`` is created on every call to
    :meth:`extract`, ensuring zero shared mutable state between
    requests.

    Args:
        settings: Application settings providing the set of heavy
            import module names.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings: Settings = settings

    def extract(self, code: str) -> ExtractedFeatures:
        """Analyze the given code and return extracted features.

        Args:
            code: Raw Python source code from the user.

        Returns:
            A fully populated ``ExtractedFeatures`` Pydantic model.

        Raises:
            CodeParsingError: If the code contains syntax errors or
                exceeds the maximum allowed length.
            AnalysisError: If an unexpected error occurs during
                AST traversal.
        """
        if len(code) > MAX_CODE_LENGTH:
            raise CodeParsingError(
                f"Input code exceeds maximum allowed length of "
                f"{MAX_CODE_LENGTH:,} characters ({len(code):,} provided)."
            )

        sanitized: str = sanitize_code_input(code)

        analyzer = CodeStructureAnalyzer(
            heavy_import_modules=self._settings.HEAVY_IMPORT_MODULES,
        )

        try:
            result = analyzer.analyze(sanitized)
        except SyntaxError as exc:
            raise CodeParsingError(
                f"Syntax error at line {exc.lineno}, column {exc.offset}: {exc.msg}"
            ) from None
        except Exception as exc:
            raise AnalysisError(
                f"Unexpected analysis failure: {type(exc).__name__}"
            ) from exc

        return ExtractedFeatures(
            max_loop_depth=result.max_loop_depth,
            has_nested_loops=result.has_nested_loops,
            function_calls_inside_loops=result.function_calls_inside_loops,
            has_recursion=result.has_recursion,
            recursion_inside_loop=result.recursion_inside_loop,
            heavy_imports_detected=sorted(result.heavy_imports),
        )
