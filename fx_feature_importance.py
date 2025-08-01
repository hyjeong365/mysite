import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.metrics import mean_absolute_error
from sklearn.inspection import permutation_importance
import xgboost as xgb

try:
    import shap  # SHAP gives model-agnostic importance values
except ImportError:
    shap = None



def load_dataset(csv_path: str, date_col: str, target_col: str):
    """Load a CSV, parse dates, set index, and return features/target."""
    df = pd.read_csv(csv_path, parse_dates=[date_col])
    df = df.sort_values(date_col)
    df.set_index(date_col, inplace=True)

    y = df[target_col]
    X = df.drop(columns=[target_col])
    return X, y


def temporal_train_test_split(X, y, test_size: float = 0.2):
    """Split keeping temporal order (no shuffling)."""
    split_idx = int(len(X) * (1 - test_size))
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    return X_train, X_test, y_train, y_test


def train_xgboost_regressor(X_train, y_train):
    params = {
        "n_estimators": 500,
        "learning_rate": 0.05,
        "max_depth": 6,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "objective": "reg:squarederror",
        "random_state": 42,
    }
    model = xgb.XGBRegressor(**params)
    model.fit(X_train, y_train, verbose=False)
    return model


def plot_builtin_importance(model, feature_names, top_n=20):
    importances = model.get_booster().get_score(importance_type="gain")
    imp_series = pd.Series(importances).reindex(feature_names).fillna(0)
    imp_series.nlargest(top_n).plot(kind="barh", figsize=(8, 6))
    plt.gca().invert_yaxis()
    plt.title("XGBoost Feature Importance (gain)")
    plt.xlabel("Total Gain")
    plt.tight_layout()
    plt.show()


def permutation_importance_plot(model, X_test, y_test, top_n=20):
    result = permutation_importance(model, X_test, y_test, n_repeats=30, random_state=42, scoring="neg_mean_absolute_error")
    sorted_idx = result.importances_mean.argsort()[::-1][:top_n]
    plt.figure(figsize=(8, 6))
    plt.barh(range(top_n), result.importances_mean[sorted_idx][::-1])
    plt.yticks(range(top_n), X_test.columns[sorted_idx][::-1])
    plt.xlabel("Permutation Importance (MAE decrease)")
    plt.title("Permutation Feature Importance")
    plt.tight_layout()
    plt.show()


def shap_summary_plot(model, X_train):
    if shap is None:
        print("SHAP is not installed. Run `pip install shap` to enable SHAP plots.")
        return
    explainer = shap.Explainer(model, X_train)
    shap_values = explainer(X_train)
    shap.summary_plot(shap_values, X_train, show=True)


def main():
    # ----- USER CONFIGURATION -----
    csv_path = "./data/exchange_rates.csv"  # path to your dataset
    date_column = "date"  # column containing dates
    target_column = "exchange_rate"  # column to predict
    # --------------------------------

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset not found at {csv_path}. Please update the path or add your CSV.")

    X, y = load_dataset(csv_path, date_column, target_column)
    X_train, X_test, y_train, y_test = temporal_train_test_split(X, y)

    model = train_xgboost_regressor(X_train, y_train)

    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    print(f"Test MAE: {mae:.4f}")

    # 1. Built-in importance (gain)
    plot_builtin_importance(model, X.columns)

    # 2. Permutation importance (model-agnostic)
    permutation_importance_plot(model, X_test, y_test)

    # 3. SHAP values (optional, provides local + global explanations)
    shap_summary_plot(model, X_train)


if __name__ == "__main__":
    main()