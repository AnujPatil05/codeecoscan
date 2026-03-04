"""Example: Nested loops with function calls inside.

This file demonstrates patterns that increase energy risk:
- Triple-nested loops (depth 3 → loop_score = 40)
- Function calls inside loops (interaction penalty = 15)

Expected risk: High
"""


def process_matrix(matrix: list[list[list[int]]]) -> list[int]:
    """Flatten a 3D matrix by summing all elements per row."""
    results: list[int] = []

    for layer in matrix:
        for row in layer:
            total = 0
            for value in row:
                total += abs(value)  # function call inside loop
            results.append(total)

    return results


if __name__ == "__main__":
    sample = [
        [[1, -2, 3], [4, 5, -6]],
        [[7, -8, 9], [10, 11, -12]],
    ]
    print(process_matrix(sample))
