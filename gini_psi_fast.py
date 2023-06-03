import pandas as pd
from sklearn.metrics import roc_auc_score

# Your DataFrame
df = pd.DataFrame({
    'target': [0, 0, 1, 1, 0, 1, 0, 1, 1, 1],
    'num_var': [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    'cat_var': ['a', 'b', 'a', 'b', 'a', 'b', 'a', 'b', 'a', 'b']
})

# Function to calculate AUC for all features
def calculate_auc(df, target):
    result = {}
    for col in df.columns:
        if col != target:
            if df[col].nunique() < 2:
                continue
            df_no_na = df[[col, target]].dropna()

            if df[col].dtype.name in ['object', 'category']:
                event_rate = df.groupby(col)[target].mean()
                temp_col = df[col].map(event_rate)
            else:  # For numerical features
                temp_col = df[col]
            result[col] = roc_auc_score(df[target], temp_col)
    return abs(result)

# Calculate AUC
auc_scores = calculate_auc(df, 'target')

# Convert dictionary to DataFrame
auc_df = pd.DataFrame(list(auc_scores.items()), columns=['variable', 'AUC'])

auc_df


# Create a crosstab
index = pd.date_range('2000', '2010', freq='A')
data = np.random.rand(10, 5)
df = pd.DataFrame(data, index=index.year, columns=['A', 'B', 'C', 'D', 'E'])
df = df.div(df.sum(axis=1), axis=0)  # Normalize the rows to get the distributions

# Calculate PSI for adjacent periods
psi_values = []
for i in range(len(df)-1):
    actual = df.iloc[i]
    expected = df.iloc[i+1]
    psi = np.sum((actual - expected) * np.log(actual / expected))
    psi_values.append(psi)

# Create a DataFrame with PSI values
psi_df = pd.DataFrame(psi_values, index=df.index[1:], columns=['PSI'])
