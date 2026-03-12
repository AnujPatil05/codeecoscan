# CodeEcoScan — Energy & Carbon Analysis for Python Code

![Python](https://img.shields.io/badge/python-3.11+-blue)
![CI](https://github.com/AnujPatil05/codeecoscan/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-green)
[![Live API](https://img.shields.io/badge/API-live%20demo-brightgreen)](https://codeecoscan.onrender.com/docs)

**Static energy-risk analysis for Python code.**
https://codeecoscan.vercel.app/

CodeEcoScan parses Python source files using the `ast` module, extracts structural patterns linked to computational cost, scores them for energy risk, and optionally estimates carbon emissions for different hardware scenarios — all without executing a single line of your code.

### Example Output

```
$ codeecoscan examples/nested_loops.py --runtime 60 --runs-per-day 10 --hardware small_cloud_vm

CodeEcoScan Analysis Report
========================================

  Energy Risk Score: 55/100  [Moderate]

  Score Breakdown:
    Loop Score                     +40
    Interaction Penalty            +15
    Recursion                       0
    Heavy Imports                   0

  Extracted Features:
    Max loop depth:              3
    Nested loops:                True
    Calls inside loops:          True
    Recursion:                   False
    Recursion inside loop:       False
    Heavy imports:               (none)

  Emissions Estimate
    Hardware:            small_cloud_vm
    Runtime:             60.0s × 10 runs/day
    Energy:              20.00 Wh/day
    CO₂:                 0.0080 kg/day
    Carbon intensity:    0.4 kg CO₂/kWh (global grid avg, IEA)
```

---

## The Problem

Software energy consumption is invisible. A triply-nested loop calling functions on every iteration, a recursive function inside a loop, or unnecessary heavy-library imports all carry real energy costs — but developers never see them. CodeEcoScan makes these costs visible and measurable.

> **Note:** CodeEcoScan produces *structural risk scores* and *scenario-based estimates*, not runtime measurements. It is a static linter for energy awareness, not a profiler.

---

## Features

| Capability | Description |
|-----------|------------|
| **AST Analysis** | Detects loop depth, nested loops, recursion, calls inside loops, heavy imports |
| **Energy Risk Scoring** | Quadratic loop formula, interaction penalties, tiered recursion scoring (0–100) |
| **Emissions Modeling** | Scenario-based CO₂ estimation with configurable hardware profiles |
| **CLI** | Colored reports, JSON output, CI-compatible `--threshold` exit codes |
| **REST API** | FastAPI endpoint (`POST /analyze`) with Swagger docs |

---

## Installation

```bash
# Clone the repository
git clone https://github.com/your-username/codeecoscan.git
cd codeecoscan

# Install dependencies
pip install -r requirements.txt

# (Optional) Install as a CLI tool
pip install -e .
```

**Requirements:** Python 3.11+

---

## CLI Usage

### Basic analysis

```bash
# Full report (colored)
python -m app.cli.main path/to/file.py

# JSON output (matches API response format)
python -m app.cli.main path/to/file.py --json

# Score only (single line)
python -m app.cli.main path/to/file.py --score-only
```

### CI integration

```bash
# Exit code 1 if score >= 70
python -m app.cli.main path/to/file.py --threshold 70
```

### Emissions estimation

```bash
# Single hardware profile
python -m app.cli.main path/to/file.py \
  --runtime 60 --runs-per-day 10 --hardware laptop

# Compare across hardware profiles
python -m app.cli.main path/to/file.py \
  --runtime 60 --runs-per-day 10 \
  --compare laptop small_cloud_vm gpu_server

# Custom carbon intensity (default: 0.4 kg CO₂/kWh)
python -m app.cli.main path/to/file.py \
  --runtime 60 --runs-per-day 10 --hardware laptop \
  --carbon-intensity 0.05
```

If installed with `pip install -e .`, use `codeecoscan` instead of `python -m app.cli.main`.

---

## API Usage

> **Live API:** [codeecoscan.onrender.com/docs](https://codeecoscan.onrender.com/docs) (Swagger UI)

```bash
# Or run locally
uvicorn app.main:app --reload --port 8000
```

### Analyze code

```bash
curl -X POST https://codeecoscan.onrender.com/analyze \
  -H "Content-Type: application/json" \
  -d '{"code": "for i in range(10):\n    for j in range(10):\n        print(i, j)"}'
```

### Example response

```json
{
  "extracted_features": {
    "max_loop_depth": 2,
    "has_nested_loops": true,
    "function_calls_inside_loops": true,
    "has_recursion": false,
    "recursion_inside_loop": false,
    "heavy_imports_detected": []
  },
  "risk_assessment": {
    "energy_risk_score": 35,
    "risk_level": "Moderate",
    "risk_breakdown": {
      "loop_score": 20,
      "interaction_penalty": 15,
      "recursion": 0,
      "heavy_imports": 0
    }
  }
}
```

Swagger UI available at: http://localhost:8000/docs

---

## Scoring Model

| Component | Formula | Max |
|-----------|---------|-----|
| Loop depth | `min(5 × depth², 40)` | 40 |
| Interaction penalty | +15 if `depth ≥ 2 AND calls_inside_loops` | 15 |
| Recursion | +10 base, +10 if inside loop | 20 |
| Heavy imports | `min(8 × count, 25)` | 25 |
| **Total** | `clamp(sum, 0, 100)` | **100** |

| Score | Risk Level |
|-------|-----------|
| 0–34 | Low |
| 35–69 | Moderate |
| 70–100 | High |

All weights are configurable in `app/scoring/scoring_rules.py`.

---

## Emissions Model

```
energy_wh_per_run  = (power_watts × runtime_seconds) / 3600
energy_wh_per_day  = energy_wh_per_run × runs_per_day
co2_kg_per_day     = (energy_wh_per_day / 1000) × carbon_intensity
```

### Built-in hardware profiles

| Profile | Power |
|---------|-------|
| `laptop` | 45 W |
| `small_cloud_vm` | 120 W |
| `gpu_server` | 300 W |

> **Disclaimer:** Emissions estimates are scenario-based approximations using constant power draw and flat grid-average carbon intensity. They are not runtime measurements.

---

## Architecture

```
Python Source Code
       ↓
  AST Analyzer         → AnalysisResult (loop depth, recursion, imports, ...)
       ↓
  Feature Extractor    → ExtractedFeatures (Pydantic model)
       ↓
  Risk Scoring Engine  → RiskAssessment (score, level, breakdown)
       ↓
  Emissions Estimator  → EmissionsEstimate (Wh/day, kg CO₂/day)
       ↓
  CLI / API Output
```

See [docs/architecture.md](docs/architecture.md) for the full architecture breakdown.

---

## Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run a specific suite
python -m pytest tests/test_scoring.py -v
```

Current: **116 tests passing**.

---

## Project Structure

```
codeecoscan/
├── app/
│   ├── analysis/          # AST analyzer + feature extractor
│   ├── scoring/           # Risk scoring engine + configurable rules
│   ├── emissions/         # Carbon estimator + hardware profiles
│   ├── cli/               # Command-line interface
│   ├── api/               # FastAPI routes
│   ├── core/              # Config + exceptions
│   ├── models/            # Pydantic schemas
│   └── utils/             # Input sanitization
├── tests/                 # 116 unit + integration tests
├── docs/                  # Architecture documentation
├── examples/              # Example Python files for testing
├── README.md
├── LICENSE
├── pyproject.toml
├── requirements.txt
└── .gitignore
```

---

## Limitations

- **Static analysis only** — does not execute code or measure actual runtime
- **Direct recursion only** — does not detect indirect recursion (`A → B → A`)
- **No runtime inference** — emissions require user-provided scenario parameters
- **No PUE modeling** — data center overhead not included in emissions
- **Single-file analysis** — cannot analyze multi-file projects or imports across modules
- **Constant power assumption** — real power draw varies with CPU/GPU utilization

---

## Roadmap

- [ ] Multi-file / project-level analysis
- [ ] Indirect recursion detection via call graph
- [ ] PUE factor for data center emissions
- [ ] Region-aware carbon intensity lookup
- [ ] Risk-weighted emissions estimation
- [ ] GitHub Action for automated PR checks
- [ ] Pre-commit hook integration
- [ ] VS Code extension

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
