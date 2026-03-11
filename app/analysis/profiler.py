"""AST-based execution cost profiler for CodeEcoScan.

Estimates relative execution cost per line using AST structure:
- Loop nodes → high cost (multiplicative with loop depth)
- Import statements → medium cost (module loading)
- Function calls → variable cost (call overhead)
- Memory operations (copy, append, etc.) → medium cost
- Simple assignments → low cost

This is NOT instrumented profiling — it's static estimation.
Results are deterministic and immediate.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from typing import Any


@dataclass
class LineProfile:
    line: int
    time_ms: float
    category: str  # 'critical' | 'warning' | 'low'


@dataclass
class FunctionProfile:
    name: str
    start_line: int
    end_line: int
    energy_uwh: float   # micro watt-hours (estimated)


@dataclass
class ProfilingResult:
    line_times: list[LineProfile] = field(default_factory=list)
    function_costs: list[FunctionProfile] = field(default_factory=list)
    peak_memory_mb: int = 0
    total_energy_uwh: float = 0.0


_MEMORY_FUNCS = {"copy", "deepcopy", "append", "extend", "tolist", "values", "keys"}
_HEAVY_FUNCS  = {"read_csv", "read_excel", "read_json", "fit", "predict", "train", "eval", "forward"}
_BASE_COSTS = {
    "For": 12.0,
    "While": 8.0,
    "Import": 5.0,
    "ImportFrom": 5.0,
    "FunctionDef": 0.5,
    "Call": 2.0,
    "Assign": 0.3,
    "AugAssign": 0.3,
    "Return": 0.2,
    "If": 0.5,
    "Expr": 0.3,
}


class _ProfileVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self._loop_depth   = 0
        self._line_costs: dict[int, float] = {}
        self._functions: list[FunctionProfile] = []
        self._heavy_memory = 0

    def _add_cost(self, lineno: int, cost: float) -> None:
        self._line_costs[lineno] = self._line_costs.get(lineno, 0.0) + cost

    def _loop_multiplier(self) -> float:
        return 10.0 ** max(self._loop_depth - 1, 0) if self._loop_depth >= 2 else max(self._loop_depth, 0.1)

    def _visit_loop(self, node: ast.AST) -> None:
        self._loop_depth += 1
        base = _BASE_COSTS["For"] * self._loop_multiplier()
        self._add_cost(node.lineno, base)
        self.generic_visit(node)
        self._loop_depth -= 1

    def visit_For(self, node: ast.For)     -> None: self._visit_loop(node)
    def visit_While(self, node: ast.While) -> None: self._visit_loop(node)
    def visit_AsyncFor(self, node: ast.AsyncFor) -> None: self._visit_loop(node)

    def visit_Import(self, node: ast.Import) -> None:
        self._add_cost(node.lineno, _BASE_COSTS["Import"])
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        self._add_cost(node.lineno, _BASE_COSTS["ImportFrom"])
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        func_name = ""
        if isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
        elif isinstance(node.func, ast.Name):
            func_name = node.func.id

        cost = _BASE_COSTS["Call"]
        if func_name in _HEAVY_FUNCS:
            cost *= 20.0
        elif func_name in _MEMORY_FUNCS:
            cost *= 5.0
            self._heavy_memory += 1
        if self._loop_depth > 0:
            cost *= self._loop_multiplier()

        self._add_cost(node.lineno, cost)
        self.generic_visit(node)

    def _visit_func(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        start = node.lineno
        end   = max((getattr(n, "lineno", start) for n in ast.walk(node)), default=start)
        self.generic_visit(node)
        # Sum costs inside the function body
        total = sum(v for ln, v in self._line_costs.items() if start <= ln <= end)
        energy = round(total * 0.001, 4)   # scale to μWh
        self._functions.append(FunctionProfile(
            name=node.name,
            start_line=start,
            end_line=end,
            energy_uwh=energy,
        ))

    def visit_FunctionDef(self, node: ast.FunctionDef)             -> None: self._visit_func(node)
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef)   -> None: self._visit_func(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        self._add_cost(node.lineno, _BASE_COSTS["Assign"])
        self.generic_visit(node)

    def visit_Return(self, node: ast.Return) -> None:
        self._add_cost(node.lineno, _BASE_COSTS["Return"])
        self.generic_visit(node)


def profile_code(code: str) -> ProfilingResult:
    """Estimate per-line execution cost from AST structure.

    Returns a ``ProfilingResult`` with line_times and function_costs.
    Never raises — returns empty result on syntax error.
    """
    if not code.strip():
        return ProfilingResult()

    try:
        tree = ast.parse(code, mode="exec")
    except SyntaxError:
        return ProfilingResult()

    visitor = _ProfileVisitor()
    visitor.visit(tree)

    total = sum(visitor._line_costs.values()) or 1.0

    line_times: list[LineProfile] = []
    for ln, cost in sorted(visitor._line_costs.items()):
        pct = cost / total
        if pct > 0.3:
            cat = "critical"
        elif pct > 0.05:
            cat = "warning"
        else:
            cat = "low"
        # Scale to ms: normalize to 0–500ms range
        time_ms = round((cost / total) * 500, 1)
        line_times.append(LineProfile(line=ln, time_ms=time_ms, category=cat))

    # Sort functions by energy descending
    fn_costs = sorted(visitor._functions, key=lambda f: f.energy_uwh, reverse=True)

    peak_memory = max(50, min(visitor._heavy_memory * 80, 800))
    total_energy = sum(f.energy_uwh for f in fn_costs)

    return ProfilingResult(
        line_times=line_times,
        function_costs=fn_costs,
        peak_memory_mb=peak_memory,
        total_energy_uwh=round(total_energy, 3),
    )
