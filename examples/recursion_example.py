"""Example: Direct recursion.

This file demonstrates recursive patterns that CodeEcoScan detects:
- Direct recursion (factorial calling itself → recursion = 10)
- Recursion inside a loop (process_tree → recursion = 20)

Expected risk: Moderate (due to recursion-inside-loop + loop depth)
"""


def factorial(n: int) -> int:
    """Classic recursive factorial — direct recursion."""
    if n <= 1:
        return 1
    return n * factorial(n - 1)


def process_tree(node: dict) -> int:
    """Recursively process a tree structure inside a loop.

    This is a high-risk pattern: recursion inside a loop body.
    """
    total = node.get("value", 0)
    for child in node.get("children", []):
        total += process_tree(child)  # recursion inside loop
    return total


if __name__ == "__main__":
    print(factorial(10))

    tree = {
        "value": 1,
        "children": [
            {"value": 2, "children": []},
            {"value": 3, "children": [
                {"value": 4, "children": []},
            ]},
        ],
    }
    print(process_tree(tree))
