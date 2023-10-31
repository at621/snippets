import numpy as np
import pandas as pd
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.inspection import permutation_importance

# Generate synthetic data
X, y = make_classification(n_samples=1000, n_features=4, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create DataFrame for easier manipulation
df_train = pd.DataFrame(X_train, columns=[f'feature_{i}' for i in range(X_train.shape[1])])
df_train['target'] = y_train

# Calculate WoE for each feature
woe_dict = {}
for feature in df_train.columns[:-1]:
    df_woe = df_train.groupby(feature).agg(
        good_count=pd.NamedAgg(column='target', aggfunc='sum'),
        total_count=pd.NamedAgg(column='feature_0', aggfunc='count')
    ).reset_index()

    df_woe['bad_count'] = df_woe['total_count'] - df_woe['good_count']
    df_woe['woe'] = np.log((df_woe['good_count'] / df_woe['good_count'].sum()) /
                            (df_woe['bad_count'] / df_woe['bad_count'].sum()))

    df_train[feature] = df_train[feature].map(df_woe.set_index(feature)['woe'])

# Fit logistic regression model
X_train_woe = df_train.drop('target', axis=1)
y_train = df_train['target']

model = LogisticRegression()
model.fit(X_train_woe, y_train)

# Calculate permutation importance
result = permutation_importance(model, X_train_woe, y_train, n_repeats=30, random_state=42)

# Calculate the sum of importances
total_importance = np.sum(result.importances_mean)

# Calculate relative importances (in percentages)
relative_importances = (result.importances_mean / total_importance) * 100

# Sort and display
sorted_idx = np.argsort(relative_importances)
for i in sorted_idx:
    print(f"{X_train_woe.columns[i]}: {relative_importances[i]:.2f}%")
