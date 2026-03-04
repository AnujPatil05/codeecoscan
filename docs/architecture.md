# CodeEcoScan — Architecture

## Pipeline Overview

```
┌─────────────────────┐
│   Python Source Code │
└─────────┬───────────┘
          ↓
┌─────────────────────┐
│    AST Analyzer      │  ast_analyzer.py
│  (ast.NodeVisitor)   │  Extracts structural patterns via visitor methods
└─────────┬───────────┘
          ↓
┌─────────────────────┐
│  Feature Extractor   │  feature_extractor.py
│  (Orchestrator)      │  Sanitizes input, creates analyzer, maps to Pydantic model
└─────────┬───────────┘
          ↓
┌─────────────────────┐
│  Risk Scoring Engine │  scoring_engine.py + scoring_rules.py
│  (Weighted formula)  │  Converts features → score (0–100) + risk level
└─────────┬───────────┘
          ↓
┌─────────────────────┐
│  Emissions Estimator │  carbon_estimator.py + hardware_profiles.py
│  (Physics-based)     │  Scenario-based energy + CO₂ calculation
└─────────┬───────────┘
          ↓
┌─────────────────────┐
│   CLI  /  FastAPI    │  cli/main.py  /  api/routes.py
│   (Output layer)     │  Format and deliver results
└─────────────────────┘
```

---

## Layer Responsibilities

### 1. AST Analyzer (`app/analysis/ast_analyzer.py`)

**Input:** Sanitized Python source code string.
**Output:** `AnalysisResult` (frozen dataclass).

The `CodeStructureAnalyzer` extends `ast.NodeVisitor` and implements visitor methods for:

| Visitor | Detects |
|---------|---------|
| `visit_For`, `visit_While`, `visit_AsyncFor` | Loop depth tracking |
| `visit_ListComp`, `visit_SetComp`, `visit_DictComp`, `visit_GeneratorExp` | Comprehension loop depth |
| `visit_FunctionDef`, `visit_AsyncFunctionDef` | Function context stack |
| `visit_Call` | Recursion, recursion-inside-loop, calls inside loops |
| `visit_Import`, `visit_ImportFrom` | Heavy import detection |

**Thread safety:** All state is instance-level and reset on each `analyze()` call.

### 2. Feature Extractor (`app/analysis/feature_extractor.py`)

Orchestrator layer between raw AST analysis and the API/CLI.

- Sanitizes input via `sanitize_code_input()`
- Enforces the 200,000-character input size guard
- Creates a fresh `CodeStructureAnalyzer` per call
- Maps `AnalysisResult` → `ExtractedFeatures` (Pydantic model)
- Translates `SyntaxError` → `CodeParsingError` (HTTP 400)

### 3. Risk Scoring Engine (`app/scoring/`)

**Input:** `ExtractedFeatures`.
**Output:** `RiskAssessment` (score, level, breakdown).

Formula:

```
loop_score          = min(5 × depth², 40)
interaction_penalty = 15    if depth ≥ 2 AND calls_inside_loops
recursion           = 10    if has_recursion
                    + 10    if recursion_inside_loop
heavy_imports       = min(8 × count, 25)
total               = clamp(sum, 0, 100)
```

All weights are stored in `scoring_rules.py` as frozen dataclasses. The scorer is framework-agnostic and stateless.

### 4. Emissions Estimator (`app/emissions/`)

**Input:** Runtime seconds, runs per day, hardware profile, carbon intensity.
**Output:** `EmissionsEstimate` (energy Wh/day, CO₂ kg/day).

Formula:

```
energy_wh_per_run  = (power_watts × runtime_seconds) / 3600
energy_wh_per_day  = energy_wh_per_run × runs_per_day
co2_kg_per_day     = (energy_wh_per_day / 1000) × carbon_intensity
```

`RiskAssessment` is accepted as a parameter but **not used** in the current formula — reserved for future risk-weighted estimation.

### 5. Output Layers

**CLI** (`app/cli/main.py`) — argparse-based, zero FastAPI dependency. Supports `--json`, `--score-only`, `--threshold`, emissions flags (`--runtime`, `--runs-per-day`, `--hardware`, `--compare`).

**API** (`app/api/routes.py`) — FastAPI `POST /analyze` endpoint. Route handler has zero business logic — delegates entirely to `FeatureExtractor` and `EnergyRiskScorer` via dependency injection.

---

## Separation of Concerns

```
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│   CLI Layer  │   │  API Layer   │   │  Future UIs  │
└──────┬───────┘   └──────┬───────┘   └──────┬───────┘
       │                  │                  │
       └──────────────────┼──────────────────┘
                          ↓
              ┌───────────────────────┐
              │   Feature Extractor   │
              │   Scoring Engine      │
              │   Emissions Estimator │
              └───────────────────────┘
                    (Framework-agnostic)
```

- **Analysis, scoring, and emissions** have zero dependency on FastAPI or argparse
- **Each layer** can be tested independently
- **Swapping FastAPI** for Flask, Django, or a CLI-only distribution requires zero changes to the core modules
- **All mutable state** is instance-level and request-scoped — no global singletons
