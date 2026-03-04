"""Example: Heavy library imports.

This file demonstrates import patterns that CodeEcoScan detects
as energy-heavy:
- torch (PyTorch)
- pandas
- sklearn (scikit-learn)

Expected: heavy_imports = min(8 × 3, 25) = 24 points
"""

import torch
import pandas as pd
from sklearn.ensemble import RandomForestClassifier


def train_model(data_path: str) -> None:
    """Placeholder training function using heavy libraries."""
    df = pd.read_csv(data_path)
    X = torch.tensor(df.iloc[:, :-1].values, dtype=torch.float32)
    y = df.iloc[:, -1].values

    clf = RandomForestClassifier(n_estimators=100)
    clf.fit(df.iloc[:, :-1], y)
    print(f"Trained on {len(y)} samples")


if __name__ == "__main__":
    train_model("data.csv")
