"""Integration tests for the /analyze API endpoint.

Uses FastAPI's ``TestClient`` (backed by ``httpx``) to exercise
the full request→response cycle including validation, exception
handling, and response schemas.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


# ------------------------------------------------------------------
# Successful analysis
# ------------------------------------------------------------------


class TestAnalyzeEndpointSuccess:
    """Happy-path tests for POST /analyze."""

    def test_simple_code(self) -> None:
        response = client.post("/analyze", json={"code": "x = 1\n"})
        assert response.status_code == 200
        body = response.json()
        assert "extracted_features" in body
        features = body["extracted_features"]
        assert features["max_loop_depth"] == 0
        assert features["has_nested_loops"] is False
        assert features["has_recursion"] is False

    def test_nested_loop_with_heavy_import(self) -> None:
        code = (
            "import torch\n"
            "for i in range(10):\n"
            "    for j in range(10):\n"
            "        pass\n"
        )
        response = client.post("/analyze", json={"code": code})
        assert response.status_code == 200
        features = response.json()["extracted_features"]
        assert features["max_loop_depth"] == 2
        assert features["has_nested_loops"] is True
        assert "torch" in features["heavy_imports_detected"]

    def test_recursive_function(self) -> None:
        code = (
            "def factorial(n):\n"
            "    if n <= 1:\n"
            "        return 1\n"
            "    return n * factorial(n - 1)\n"
        )
        response = client.post("/analyze", json={"code": code})
        assert response.status_code == 200
        features = response.json()["extracted_features"]
        assert features["has_recursion"] is True

    def test_function_call_inside_loop(self) -> None:
        code = "for i in range(5):\n    print(i)\n"
        response = client.post("/analyze", json={"code": code})
        assert response.status_code == 200
        features = response.json()["extracted_features"]
        assert features["function_calls_inside_loops"] is True

    def test_multiple_heavy_imports(self) -> None:
        code = (
            "import tensorflow\n"
            "from torch.nn import Linear\n"
            "from sklearn.ensemble import RandomForestClassifier\n"
        )
        response = client.post("/analyze", json={"code": code})
        assert response.status_code == 200
        imports = response.json()["extracted_features"]["heavy_imports_detected"]
        assert sorted(imports) == ["sklearn", "tensorflow", "torch"]


# ------------------------------------------------------------------
# Error handling
# ------------------------------------------------------------------


class TestAnalyzeEndpointErrors:
    """Error-path tests for POST /analyze."""

    def test_syntax_error_returns_400(self) -> None:
        response = client.post("/analyze", json={"code": "def foo(:\n    pass"})
        assert response.status_code == 400
        body = response.json()
        assert "detail" in body
        assert "Syntax error" in body["detail"]

    def test_empty_code_returns_422(self) -> None:
        response = client.post("/analyze", json={"code": ""})
        assert response.status_code == 422

    def test_missing_code_field_returns_422(self) -> None:
        response = client.post("/analyze", json={})
        assert response.status_code == 422

    def test_oversized_input_returns_400(self) -> None:
        """Code exceeding 200,000 characters must be rejected."""
        code = "x = 1\n" * 100_001  # ~600k chars
        response = client.post("/analyze", json={"code": code})
        assert response.status_code == 400
        body = response.json()
        assert "detail" in body
        assert "maximum allowed length" in body["detail"]

    def test_whitespace_only_returns_200_zeroed(self) -> None:
        """Whitespace-only code is valid but produces zero features."""
        response = client.post("/analyze", json={"code": "   \n  \n  "})
        assert response.status_code == 200
        features = response.json()["extracted_features"]
        assert features["max_loop_depth"] == 0
        assert features["has_nested_loops"] is False
        assert features["has_recursion"] is False
        assert features["function_calls_inside_loops"] is False
        assert features["heavy_imports_detected"] == []


# ------------------------------------------------------------------
# Health check
# ------------------------------------------------------------------


class TestHealthEndpoint:
    """Health check must always return 200."""

    def test_health_returns_healthy(self) -> None:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
