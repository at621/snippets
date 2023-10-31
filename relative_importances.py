import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.inspection import permutation_importance

# Simulate WoE values for features and target
np.random.seed(42)
n_samples = 1000
n_features = 4

# Simulating WoE-transformed features
X_train_woe = pd.DataFrame(np.random.randn(n_samples, n_features), columns=[f'feature_{i}' for i in range(n_features)])
y_train = np.random.randint(2, size=n_samples)

# Fit logistic regression model
model = LogisticRegression()
model.fit(X_train_woe, y_train)

# Calculate permutation importance
result = permutation_importance(model, X_train_woe, y_train, n_repeats=30, random_state=42)

# Calculate the sum of importances
total_importance = np.sum(result.importances_mean)

# Check for problematic total_importance values
if total_importance == 0 or np.isnan(total_importance):
    print("Total importance is zero or NaN.")
else:
    # Calculate relative importances (in percentages)
    try:
        relative_importances = (result.importances_mean / total_importance) * 100
    except Exception as e:
        print(f"An error occurred while calculating relative importances: {e}")

    # Sort and display
    sorted_idx = np.argsort(relative_importances)
    for i in sorted_idx:
        print(f"{X_train_woe.columns[i]}: {relative_importances[i]:.2f}%")
