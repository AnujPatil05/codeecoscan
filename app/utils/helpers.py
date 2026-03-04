"""Shared utility functions for CodeEcoScan.

Stateless helpers that perform input sanitization and other
cross-cutting concerns.
"""


def sanitize_code_input(code: str) -> str:
    """Prepare raw user code for safe ``ast.parse`` consumption.

    Performs the following transformations:

    1. Strips trailing whitespace from each line.
    2. Ensures the code ends with exactly one newline (required by
       ``ast.parse`` for consistent behavior with some edge cases).
    3. Returns an empty string if the input is whitespace-only, allowing
       the caller to handle empty input gracefully.

    Args:
        code: Raw source code string from the user.

    Returns:
        Sanitized code string ready for parsing.
    """
    stripped: str = "\n".join(line.rstrip() for line in code.splitlines())
    stripped = stripped.strip()
    if not stripped:
        return ""
    return stripped + "\n"
