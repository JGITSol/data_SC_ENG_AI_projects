import pandas as pd
import numpy as np
from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import joblib

# Generate synthetic data for demo
X, y = make_regression(n_samples=200, n_features=5, noise=0.1, random_state=42)
df = pd.DataFrame(X, columns=[f"feature_{i}" for i in range(X.shape[1])])
df["target"] = y

# Split data
X_train, X_test, y_train, y_test = train_test_split(df.drop("target", axis=1), df["target"], test_size=0.2, random_state=42)

# Train model
model = LinearRegression()
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
print(f"Test MSE: {mse:.2f}")

import os
model_path = os.path.join(os.path.dirname(__file__), "model.joblib")
joblib.dump(model, model_path)

# Save test sample for API demo
X_test.iloc[:5].to_json("sample_input.json", orient="records")
