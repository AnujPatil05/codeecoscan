"""AST-based code structure analyzer.

Implements the visitor pattern via ``ast.NodeVisitor`` to extract
structural features from Python source code without executing it.

This module is the lowest layer of the analysis engine — it deals
exclusively with AST traversal and populates a raw ``AnalysisResult``
dataclass.  It has no knowledge of HTTP, Pydantic schemas, or
application configuration.

Thread-safety guarantee
-----------------------
``CodeStructureAnalyzer`` stores all mutable state as *instance*
attributes that are reset on every call to ``analyze()``.  There is
no module-level or class-level mutable state.  A fresh instance is
created per request by the ``FeatureExtractor`` layer, so concurrent
FastAPI requests never share mutable state.

Usage example (in-comment unit-test style)
------------------------------------------
**Nested loop detection:**

>>> analyzer = CodeStructureAnalyzer(heavy_import_modules=frozenset())
>>> result = analyzer.analyze('''
... for i in range(10):
...     for j in range(10):
...         pass
... ''')
>>> result.max_loop_depth
2
>>> result.has_nested_loops
True

**Recursion detection:**

>>> analyzer = CodeStructureAnalyzer(heavy_import_modules=frozenset())
>>> result = analyzer.analyze('''
... def factorial(n):
...     if n <= 1:
...         return 1
...     return n * factorial(n - 1)
... ''')
>>> result.has_recursion
True
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class AnalysisResult:
    """Immutable container for raw AST analysis findings.

    Attributes:
        max_loop_depth: Deepest observed loop nesting level.
        has_nested_loops: Whether any loop is nested inside another.
        function_calls_inside_loops: Whether any ``ast.Call`` appears
            inside a loop body.
        has_recursion: Whether direct recursion was detected.
        recursion_inside_loop: Whether a recursive call occurs inside
            a loop body (``_current_loop_depth > 0`` at detection time).
        heavy_imports: Set of detected heavy-import module names.
    """

    max_loop_depth: int = 0
    has_nested_loops: bool = False
    function_calls_inside_loops: bool = False
    has_recursion: bool = False
    recursion_inside_loop: bool = False
    heavy_imports: frozenset[str] = field(default_factory=frozenset)


class CodeStructureAnalyzer(ast.NodeVisitor):
    """Stateless AST visitor that extracts structural code features.

    Each call to :meth:`analyze` resets internal counters so that the
    instance can theoretically be reused — though the recommended
    pattern is one instance per request.

    Args:
        heavy_import_modules: Frozen set of top-level module names
            considered energy-heavy (e.g. ``{"torch", "tensorflow"}``).
    """

    def __init__(self, heavy_import_modules: frozenset[str]) -> None:
        self._heavy_import_modules: frozenset[str] = heavy_import_modules
        self._reset()

    # ------------------------------------------------------------------
    # Internal state management
    # ------------------------------------------------------------------

    def _reset(self) -> None:
        """Reset all mutable traversal state to initial values."""
        self._current_loop_depth: int = 0
        self._max_loop_depth: int = 0
        self._has_nested_loops: bool = False
        self._function_calls_inside_loops: bool = False
        self._has_recursion: bool = False
        self._recursion_inside_loop: bool = False
        self._heavy_imports: set[str] = set()
        self._function_context_stack: list[str] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyze(self, code: str) -> AnalysisResult:
        """Parse and analyze the given Python source code.

        Args:
            code: Sanitized Python source code string.  An empty
                string is valid and produces a zeroed-out result.

        Returns:
            An immutable ``AnalysisResult`` with the extracted features.

        Raises:
            SyntaxError: If ``ast.parse`` cannot parse the code.  The
                caller (``FeatureExtractor``) is responsible for
                converting this into a ``CodeParsingError``.
        """
        self._reset()

        if not code.strip():
            return AnalysisResult()

        tree: ast.Module = ast.parse(code, mode="exec")
        self.visit(tree)

        return AnalysisResult(
            max_loop_depth=self._max_loop_depth,
            has_nested_loops=self._has_nested_loops,
            function_calls_inside_loops=self._function_calls_inside_loops,
            has_recursion=self._has_recursion,
            recursion_inside_loop=self._recursion_inside_loop,
            heavy_imports=frozenset(self._heavy_imports),
        )

    # ------------------------------------------------------------------
    # Loop visitors
    # ------------------------------------------------------------------

    def _visit_loop_node(self, node: ast.AST) -> None:
        """Shared handler for all loop node types.

        Increments loop depth *before* visiting children and decrements
        *after*, guaranteeing accurate max-depth tracking regardless of
        nesting shape.
        """
        self._current_loop_depth += 1

        if self._current_loop_depth > self._max_loop_depth:
            self._max_loop_depth = self._current_loop_depth

        if self._current_loop_depth >= 2:
            self._has_nested_loops = True

        self.generic_visit(node)

        self._current_loop_depth -= 1

    def visit_For(self, node: ast.For) -> None:
        """Visit a ``for`` loop node."""
        self._visit_loop_node(node)

    def visit_While(self, node: ast.While) -> None:
        """Visit a ``while`` loop node."""
        self._visit_loop_node(node)

    def visit_AsyncFor(self, node: ast.AsyncFor) -> None:
        """Visit an ``async for`` loop node."""
        self._visit_loop_node(node)

    # ------------------------------------------------------------------
    # Comprehension visitors
    # ------------------------------------------------------------------

    def _visit_comprehension_node(
        self,
        node: ast.ListComp | ast.SetComp | ast.DictComp | ast.GeneratorExp,
    ) -> None:
        """Shared handler for all comprehension node types.

        Each ``comprehension`` object in ``node.generators`` represents
        one ``for`` clause.  Multi-generator comprehensions like
        ``[x for a in A for b in B]`` have two generators and reach
        loop depth 2, matching the semantics of two nested ``for``
        loops.

        The element expression (``node.elt`` / ``node.key``+``node.value``)
        is a child of the comprehension node and will be visited by
        ``generic_visit`` on the innermost generator, so calls inside
        the expression body are correctly detected at the right depth.

        For nested comprehensions (e.g. a ``ListComp`` whose ``elt``
        is another ``ListComp``), the inner comprehension's visitor
        runs while the outer generators' depth increments are still
        active, so depths compound naturally.
        """
        for generator in node.generators:
            self._current_loop_depth += 1

            if self._current_loop_depth > self._max_loop_depth:
                self._max_loop_depth = self._current_loop_depth

            if self._current_loop_depth >= 2:
                self._has_nested_loops = True

        # Visit all children (elt/key/value, conditions, sub-nodes)
        self.generic_visit(node)

        # Decrement once per generator after children are visited
        for _ in node.generators:
            self._current_loop_depth -= 1

    def visit_ListComp(self, node: ast.ListComp) -> None:
        """Visit a list comprehension node."""
        self._visit_comprehension_node(node)

    def visit_SetComp(self, node: ast.SetComp) -> None:
        """Visit a set comprehension node."""
        self._visit_comprehension_node(node)

    def visit_DictComp(self, node: ast.DictComp) -> None:
        """Visit a dict comprehension node."""
        self._visit_comprehension_node(node)

    def visit_GeneratorExp(self, node: ast.GeneratorExp) -> None:
        """Visit a generator expression node."""
        self._visit_comprehension_node(node)

    # ------------------------------------------------------------------
    # Function definition visitors (recursion context tracking)
    # ------------------------------------------------------------------

    def _visit_function_def(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        """Shared handler for function/async-function definitions.

        Pushes the function name onto the context stack before visiting
        the function body, and pops it after.  This allows nested
        function definitions to be handled correctly — the top of the
        stack always reflects the *innermost* enclosing function.
        """
        self._function_context_stack.append(node.name)
        self.generic_visit(node)
        self._function_context_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit a function definition node."""
        self._visit_function_def(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visit an async function definition node."""
        self._visit_function_def(node)

    # ------------------------------------------------------------------
    # Call visitor (recursion + calls-inside-loops detection)
    # ------------------------------------------------------------------

    def visit_Call(self, node: ast.Call) -> None:
        """Visit a function call node.

        Detects:
        1. **Direct recursion** — the call target is a bare
           ``ast.Name`` whose ``id`` matches the name at the top of
           ``_function_context_stack``.  Using only ``ast.Name``
           (not ``ast.Attribute``) avoids false positives from
           ``module.func()`` calls.  Using ``stack[-1]`` (the
           *innermost* enclosing function) ensures nested functions
           calling their parent are not misclassified.
        2. **Function calls inside loops** — any ``Call`` node
           visited while ``_current_loop_depth > 0``.
        """
        # Recursion detection
        if (
            self._function_context_stack
            and isinstance(node.func, ast.Name)
            and node.func.id == self._function_context_stack[-1]
        ):
            self._has_recursion = True
            if self._current_loop_depth > 0:
                self._recursion_inside_loop = True

        # Calls inside loops detection
        if self._current_loop_depth > 0:
            self._function_calls_inside_loops = True

        self.generic_visit(node)

    # ------------------------------------------------------------------
    # Import visitors (heavy-import detection)
    # ------------------------------------------------------------------

    def visit_Import(self, node: ast.Import) -> None:
        """Visit an ``import`` statement.

        Handles statements like ``import torch``,
        ``import torch.nn``, and ``import torch as t``.
        Detection is based on the top-level module name
        (``name.split('.')[0]``), so aliases are irrelevant.
        """
        for alias in node.names:
            top_level: str = alias.name.split(".")[0]
            if top_level in self._heavy_import_modules:
                self._heavy_imports.add(top_level)

        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Visit a ``from … import`` statement.

        Handles statements like ``from torch.nn import Linear``,
        ``from sklearn.ensemble import RandomForestClassifier``, and
        ``from pandas import DataFrame as DF``.

        ``node.module`` can be ``None`` for relative imports
        (e.g. ``from . import foo``), which are safely skipped.
        """
        if node.module is not None:
            top_level: str = node.module.split(".")[0]
            if top_level in self._heavy_import_modules:
                self._heavy_imports.add(top_level)

        self.generic_visit(node)
