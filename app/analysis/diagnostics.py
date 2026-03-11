"""Line-level diagnostic extractor.

Runs a second AST pass over the parsed tree to extract line numbers
for specific patterns: nested loops, function calls inside loops,
heavy imports, and recursion.  Returns a list of ``DiagnosticIssue``
objects suitable for the API response.

This module is intentionally separate from the core AST analyzer so
that the existing scoring logic is not touched.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from app.models.schemas import DiagnosticIssue

if TYPE_CHECKING:
    from app.models.schemas import ExtractedFeatures


_HEAVY_IMPORT_SEVERITY = "medium"
_NESTED_LOOP_SEVERITY = "high"
_CALL_IN_LOOP_SEVERITY = "medium"
_RECURSION_SEVERITY = "medium"


class _DiagnosticVisitor(ast.NodeVisitor):
    """AST visitor that records issue locations with line numbers."""

    def __init__(self, heavy_modules: frozenset[str]) -> None:
        self._heavy = heavy_modules
        self._loop_depth = 0
        self._func_stack: list[str] = []
        self._issues: list[DiagnosticIssue] = []
        self._seen_nested_lines: set[int] = set()
        self._seen_call_lines: set[int] = set()

    # ── Helpers ───────────────────────────────────────

    def _add(self, line: int, type_: str, severity: str, message: str) -> None:
        self._issues.append(DiagnosticIssue(line=line, type=type_, severity=severity, message=message))

    # ── Loops ─────────────────────────────────────────

    def _visit_loop(self, node: ast.AST) -> None:
        self._loop_depth += 1
        if self._loop_depth >= 2 and node.lineno not in self._seen_nested_lines:
            self._seen_nested_lines.add(node.lineno)
            self._add(
                node.lineno,
                "nested_loop",
                _NESTED_LOOP_SEVERITY,
                f"Nested loop depth {self._loop_depth} — O(N^{self._loop_depth}) complexity",
            )
        self.generic_visit(node)
        self._loop_depth -= 1

    def visit_For(self, node: ast.For) -> None:
        self._visit_loop(node)

    def visit_While(self, node: ast.While) -> None:
        self._visit_loop(node)

    def visit_AsyncFor(self, node: ast.AsyncFor) -> None:
        self._visit_loop(node)

    # ── Functions ─────────────────────────────────────

    def _visit_func(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        self._func_stack.append(node.name)
        self.generic_visit(node)
        self._func_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_func(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_func(node)

    # ── Calls ─────────────────────────────────────────

    def visit_Call(self, node: ast.Call) -> None:
        if self._func_stack and isinstance(node.func, ast.Name):
            if node.func.id == self._func_stack[-1]:
                sev = "high" if self._loop_depth > 0 else _RECURSION_SEVERITY
                msg = "Recursive call" + (" inside loop — exponential risk" if self._loop_depth > 0 else " detected")
                self._add(node.lineno, "recursion", sev, msg)

        if self._loop_depth > 0 and node.lineno not in self._seen_call_lines:
            self._seen_call_lines.add(node.lineno)
            self._add(
                node.lineno,
                "call_in_loop",
                _CALL_IN_LOOP_SEVERITY,
                "Function call inside loop — consider hoisting or caching",
            )

        self.generic_visit(node)

    # ── Imports ───────────────────────────────────────

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            if alias.name.split(".")[0] in self._heavy:
                self._add(
                    node.lineno,
                    "heavy_import",
                    _HEAVY_IMPORT_SEVERITY,
                    f"Heavy library '{alias.name.split('.')[0]}' — verify GPU/ML usage is required",
                )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module and node.module.split(".")[0] in self._heavy:
            self._add(
                node.lineno,
                "heavy_import",
                _HEAVY_IMPORT_SEVERITY,
                f"Heavy library '{node.module.split('.')[0]}' — verify GPU/ML usage is required",
            )
        self.generic_visit(node)


def extract_diagnostic_issues(
    code: str,
    heavy_modules: frozenset[str],
) -> list[DiagnosticIssue]:
    """Return a sorted list of line-level diagnostic issues for the given code.

    Args:
        code: Sanitized Python source code.
        heavy_modules: Set of heavy-import module names.

    Returns:
        List of ``DiagnosticIssue`` objects sorted by line number.
    """
    if not code.strip():
        return []
    try:
        tree = ast.parse(code, mode="exec")
    except SyntaxError:
        return []

    visitor = _DiagnosticVisitor(frozenset(heavy_modules))
    visitor.visit(tree)
    return sorted(visitor._issues, key=lambda i: i.line)
