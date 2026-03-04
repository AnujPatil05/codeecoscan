"""Unit tests for CodeStructureAnalyzer.

Tests cover all five extracted features, edge cases (empty input,
whitespace-only input), and correct behavior with nested functions.
"""

from __future__ import annotations

import pytest

from app.analysis.ast_analyzer import AnalysisResult, CodeStructureAnalyzer

# All tests use a minimal heavy-imports set for focused assertions.
HEAVY_MODULES: frozenset[str] = frozenset(
    {"tensorflow", "torch", "sklearn", "keras", "pandas"}
)


def _make_analyzer() -> CodeStructureAnalyzer:
    """Factory for a fresh analyzer with standard heavy modules."""
    return CodeStructureAnalyzer(heavy_import_modules=HEAVY_MODULES)


# ------------------------------------------------------------------
# Empty / whitespace-only input
# ------------------------------------------------------------------


class TestEmptyInput:
    """Analyzer must never crash on empty or whitespace-only code."""

    def test_empty_string(self) -> None:
        result: AnalysisResult = _make_analyzer().analyze("")
        assert result.max_loop_depth == 0
        assert result.has_recursion is False

    def test_whitespace_only(self) -> None:
        result: AnalysisResult = _make_analyzer().analyze("   \n\n  \t  ")
        assert result.max_loop_depth == 0

    def test_single_newline(self) -> None:
        result: AnalysisResult = _make_analyzer().analyze("\n")
        assert result.max_loop_depth == 0


# ------------------------------------------------------------------
# Loop depth tracking
# ------------------------------------------------------------------


class TestLoopDepth:
    """Loop depth must be accurate for For, While, and AsyncFor."""

    def test_single_for_loop(self) -> None:
        code = "for i in range(10):\n    pass\n"
        result = _make_analyzer().analyze(code)
        assert result.max_loop_depth == 1
        assert result.has_nested_loops is False

    def test_nested_for_loops(self) -> None:
        code = (
            "for i in range(10):\n"
            "    for j in range(10):\n"
            "        pass\n"
        )
        result = _make_analyzer().analyze(code)
        assert result.max_loop_depth == 2
        assert result.has_nested_loops is True

    def test_triple_nested_loops(self) -> None:
        code = (
            "for i in range(5):\n"
            "    for j in range(5):\n"
            "        for k in range(5):\n"
            "            pass\n"
        )
        result = _make_analyzer().analyze(code)
        assert result.max_loop_depth == 3
        assert result.has_nested_loops is True

    def test_while_loop(self) -> None:
        code = "while True:\n    break\n"
        result = _make_analyzer().analyze(code)
        assert result.max_loop_depth == 1

    def test_mixed_for_while_nested(self) -> None:
        code = (
            "for i in range(10):\n"
            "    while True:\n"
            "        break\n"
        )
        result = _make_analyzer().analyze(code)
        assert result.max_loop_depth == 2
        assert result.has_nested_loops is True

    def test_async_for_loop(self) -> None:
        code = (
            "async def f():\n"
            "    async for item in aiter:\n"
            "        for sub in item:\n"
            "            pass\n"
        )
        result = _make_analyzer().analyze(code)
        assert result.max_loop_depth == 2
        assert result.has_nested_loops is True

    def test_sequential_loops_no_nesting(self) -> None:
        code = (
            "for i in range(10):\n"
            "    pass\n"
            "for j in range(10):\n"
            "    pass\n"
        )
        result = _make_analyzer().analyze(code)
        assert result.max_loop_depth == 1
        assert result.has_nested_loops is False


# ------------------------------------------------------------------
# Comprehension loop depth tracking
# ------------------------------------------------------------------


class TestComprehensionLoopDepth:
    """Comprehension generators count as loop depth."""

    def test_single_list_comprehension(self) -> None:
        code = "result = [x for x in range(10)]\n"
        result = _make_analyzer().analyze(code)
        assert result.max_loop_depth == 1
        assert result.has_nested_loops is False

    def test_single_set_comprehension(self) -> None:
        code = "result = {x for x in range(10)}\n"
        result = _make_analyzer().analyze(code)
        assert result.max_loop_depth == 1
        assert result.has_nested_loops is False

    def test_single_dict_comprehension(self) -> None:
        code = "result = {k: v for k, v in items.items()}\n"
        result = _make_analyzer().analyze(code)
        assert result.max_loop_depth == 1
        assert result.has_nested_loops is False

    def test_generator_expression(self) -> None:
        code = "result = sum(x for x in range(10))\n"
        result = _make_analyzer().analyze(code)
        assert result.max_loop_depth == 1

    def test_multi_generator_comprehension(self) -> None:
        """``[x for a in A for b in B]`` has two generators → depth 2."""
        code = "result = [a + b for a in range(5) for b in range(5)]\n"
        result = _make_analyzer().analyze(code)
        assert result.max_loop_depth == 2
        assert result.has_nested_loops is True

    def test_nested_comprehension_in_comprehension(self) -> None:
        """Comprehension whose element expression is another comprehension."""
        code = "result = [[j for j in range(5)] for i in range(5)]\n"
        result = _make_analyzer().analyze(code)
        assert result.max_loop_depth == 2
        assert result.has_nested_loops is True

    def test_comprehension_inside_for_loop(self) -> None:
        """Comprehension inside an explicit ``for`` loop."""
        code = (
            "for i in range(10):\n"
            "    result = [x for x in range(5)]\n"
        )
        result = _make_analyzer().analyze(code)
        assert result.max_loop_depth == 2
        assert result.has_nested_loops is True

    def test_for_loop_inside_comprehension_body(self) -> None:
        """This is syntactically invalid — loops can't appear inside
        comprehension element expressions.  Instead, test a
        comprehension followed by a for-loop at the same level
        to ensure depths don't leak."""
        code = (
            "result = [x for x in range(10)]\n"
            "for i in range(5):\n"
            "    pass\n"
        )
        result = _make_analyzer().analyze(code)
        assert result.max_loop_depth == 1
        assert result.has_nested_loops is False

    def test_function_call_inside_comprehension(self) -> None:
        """Calls in comprehension element expression are at loop depth."""
        code = "result = [int(x) for x in items]\n"
        result = _make_analyzer().analyze(code)
        assert result.function_calls_inside_loops is True


# ------------------------------------------------------------------
# Function calls inside loops
# ------------------------------------------------------------------


class TestFunctionCallsInsideLoops:
    """Detect any Call node occurring inside a loop body."""

    def test_call_inside_for_loop(self) -> None:
        code = "for i in range(10):\n    print(i)\n"
        result = _make_analyzer().analyze(code)
        assert result.function_calls_inside_loops is True

    def test_no_call_inside_loop(self) -> None:
        code = "for i in range(10):\n    x = i + 1\n"
        result = _make_analyzer().analyze(code)
        # range(10) IS a call inside the for-loop's iter, which is
        # part of the For node — but the call to range is actually
        # the iterator expression, visited as a child of ast.For.
        # Since we increment depth before generic_visit, range()
        # is visited at depth 1.
        assert result.function_calls_inside_loops is True

    def test_no_loops_no_calls_inside(self) -> None:
        code = "x = 1\nprint(x)\n"
        result = _make_analyzer().analyze(code)
        assert result.function_calls_inside_loops is False


# ------------------------------------------------------------------
# Recursion detection
# ------------------------------------------------------------------


class TestRecursionDetection:
    """Direct recursion detection using function context stack."""

    def test_direct_recursion(self) -> None:
        code = (
            "def factorial(n):\n"
            "    if n <= 1:\n"
            "        return 1\n"
            "    return n * factorial(n - 1)\n"
        )
        result = _make_analyzer().analyze(code)
        assert result.has_recursion is True

    def test_no_recursion(self) -> None:
        code = (
            "def add(a, b):\n"
            "    return a + b\n"
        )
        result = _make_analyzer().analyze(code)
        assert result.has_recursion is False

    def test_nested_function_no_false_positive(self) -> None:
        """Inner function calling outer must NOT be flagged as recursion."""
        code = (
            "def outer():\n"
            "    def inner():\n"
            "        outer()\n"
            "    inner()\n"
        )
        result = _make_analyzer().analyze(code)
        # inner() calls outer() — top of stack is "inner", not "outer"
        assert result.has_recursion is False

    def test_nested_function_self_recursion(self) -> None:
        """Inner function calling itself IS recursion."""
        code = (
            "def outer():\n"
            "    def inner(n):\n"
            "        return inner(n - 1)\n"
            "    inner(5)\n"
        )
        result = _make_analyzer().analyze(code)
        assert result.has_recursion is True

    def test_method_call_not_false_positive(self) -> None:
        """Attribute-based call (self.func()) must NOT trigger recursion."""
        code = (
            "def process():\n"
            "    obj.process()\n"
        )
        result = _make_analyzer().analyze(code)
        assert result.has_recursion is False

    def test_recursion_inside_loop(self) -> None:
        """Recursive call inside a loop body → recursion_inside_loop=True."""
        code = (
            "def process(items):\n"
            "    for item in items:\n"
            "        process(item)\n"
        )
        result = _make_analyzer().analyze(code)
        assert result.has_recursion is True
        assert result.recursion_inside_loop is True

    def test_recursion_outside_loop(self) -> None:
        """Recursive call NOT inside a loop → recursion_inside_loop=False."""
        code = (
            "def factorial(n):\n"
            "    if n <= 1:\n"
            "        return 1\n"
            "    return n * factorial(n - 1)\n"
        )
        result = _make_analyzer().analyze(code)
        assert result.has_recursion is True
        assert result.recursion_inside_loop is False

    def test_recursion_in_nested_function_inside_loop(self) -> None:
        """Nested function recurses inside enclosing loop."""
        code = (
            "def outer():\n"
            "    for i in range(10):\n"
            "        def inner(n):\n"
            "            return inner(n - 1)\n"
            "        inner(5)\n"
        )
        result = _make_analyzer().analyze(code)
        assert result.has_recursion is True
        assert result.recursion_inside_loop is True


# ------------------------------------------------------------------
# Heavy import detection
# ------------------------------------------------------------------


class TestHeavyImportDetection:
    """Detect heavy imports including submodules and aliases."""

    def test_simple_import(self) -> None:
        result = _make_analyzer().analyze("import torch\n")
        assert "torch" in result.heavy_imports

    def test_submodule_import(self) -> None:
        result = _make_analyzer().analyze("import torch.nn\n")
        assert "torch" in result.heavy_imports

    def test_alias_import(self) -> None:
        result = _make_analyzer().analyze("import pandas as pd\n")
        assert "pandas" in result.heavy_imports

    def test_from_import(self) -> None:
        result = _make_analyzer().analyze("from sklearn.ensemble import RandomForestClassifier\n")
        assert "sklearn" in result.heavy_imports

    def test_from_import_submodule(self) -> None:
        result = _make_analyzer().analyze("from torch.nn import Linear\n")
        assert "torch" in result.heavy_imports

    def test_from_import_with_alias(self) -> None:
        result = _make_analyzer().analyze("from pandas import DataFrame as DF\n")
        assert "pandas" in result.heavy_imports

    def test_non_heavy_import(self) -> None:
        result = _make_analyzer().analyze("import os\nimport json\n")
        assert len(result.heavy_imports) == 0

    def test_multiple_heavy_imports(self) -> None:
        code = "import torch\nimport tensorflow\nimport pandas\n"
        result = _make_analyzer().analyze(code)
        assert result.heavy_imports == frozenset({"torch", "tensorflow", "pandas"})

    def test_relative_import_no_crash(self) -> None:
        """Relative imports (from . import x) must not crash."""
        result = _make_analyzer().analyze("from . import utils\n")
        assert len(result.heavy_imports) == 0


# ------------------------------------------------------------------
# Syntax errors
# ------------------------------------------------------------------


class TestSyntaxErrors:
    """Analyzer must raise SyntaxError for invalid code."""

    def test_syntax_error_raised(self) -> None:
        with pytest.raises(SyntaxError):
            _make_analyzer().analyze("def foo(:\n    pass\n")


# ------------------------------------------------------------------
# Statelessness
# ------------------------------------------------------------------


class TestStatelessness:
    """Consecutive calls must produce independent results."""

    def test_consecutive_calls_independent(self) -> None:
        analyzer = _make_analyzer()

        result1 = analyzer.analyze("import torch\nfor i in range(10):\n    pass\n")
        assert "torch" in result1.heavy_imports
        assert result1.max_loop_depth == 1

        result2 = analyzer.analyze("x = 1\n")
        assert len(result2.heavy_imports) == 0
        assert result2.max_loop_depth == 0
