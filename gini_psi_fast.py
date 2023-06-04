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


# Create a dummy DataFrame
data = {
    'report_date': pd.date_range(start='2022-01-01', periods=10).tolist() * 6,
    'days_in_arrears': [5, 20, 10, 70, 40, 50, 80, 30, 90, 15]*6
}

df = pd.DataFrame(data)

# Define the bucketing and checking function
def bucketing_and_check(df):
    # Define bins and labels for the pd.cut
    bins = [0, 10, 30, 60, np.inf]
    labels = ['10_days_bucket', '30_days_bucket', '60_days_bucket', '90_days_bucket']
    df['bucket'] = pd.cut(df['days_in_arrears'], bins=bins, labels=labels)
    
    # Create a cross-tabulation
    bucketed_df = pd.crosstab(df['bucket'], df['report_date'])

    # Check if columns are monotonically increasing
    non_monotonic_columns = 0
    for column in bucketed_df.columns:
        if not bucketed_df[column].is_monotonic:
            non_monotonic_columns += 1

    # Calculate the share of non-monotonic columns
    non_monotonic_share = non_monotonic_columns / len(bucketed_df.columns)

    print(f"Share of non-monotonic columns: {non_monotonic_share * 100}%")
    
    return bucketed_df

# Use the function on the dummy DataFrame
bucketed_df = bucketing_and_check(df)


def get_month_counts(df, date_column, id_column):
    # Convert to datetime if not already
    df[date_column] = pd.to_datetime(df[date_column])
   
    # Calculate the number of actual months for each contract
    actual_months = df.groupby(id_column)[date_column].nunique()
   
    # Calculate the expected number of months for each contract
    expected_months = df.groupby(id_column)[date_column].agg(lambda x: x.max() - x.min()).dt.to_period('M') + 1
   
    # Create a new DataFrame with the results
    result_df = pd.DataFrame({
        'actual_months': actual_months,
        'expected_months': expected_months
    })

    return result_df

df_month_counts = get_month_counts(df, 'date', 'contract_id')

inconsistent_contracts = df_month_counts[df_month_counts['actual_months'] != df_month_counts['expected_months']]

--------------------------------

import pandas as pd

def check_utp_sum(df, flag_column):
    # Find columns that start with 'utp'
    utp_columns = [col for col in df.columns if col.startswith('utp')]
   
    # Calculate the sum of the 'utp' columns for each row
    utp_sum = df[utp_columns].sum(axis=1)
   
    # Check if the sum is larger than the 'flag' column value
    larger_than_flag = utp_sum > df[flag_column]
   
    # If there are any rows where the 'utp' sum is larger than the 'flag' value, raise an error
    if larger_than_flag.any():
        raise ValueError(f'There are {larger_than_flag.sum()} rows where the sum of "utp" columns is larger than the "{flag_column}" value.')
    else:
        print('All rows have "utp" column sum less than or equal to the "flag" column value.')

check_utp_sum(df, 'flag')

def check_event_dates(df, date_column, event_date_column):
    # Convert to datetime if not already
    df[date_column] = pd.to_datetime(df[date_column])
    df[event_date_column] = pd.to_datetime(df[event_date_column])
   
    # Check if the event date is not earlier than the date
    event_earlier_than_date = df[event_date_column] < df[date_column]
   
    # Check if the event date is more than 12 months into the future from date
    event_more_than_year_future = df[event_date_column] > (df[date_column] + pd.DateOffset(months=12))
   
    # If there are any rows that do not meet the conditions, raise an error
    if event_earlier_than_date.any():
        raise ValueError(f'There are {event_earlier_than_date.sum()} rows where the event date is earlier than the date.')
    elif event_more_than_year_future.any():
        raise ValueError(f'There are {event_more_than_year_future.sum()} rows where the event date is more than 12 months into the future from date.')
    else:
        print('All rows meet the date conditions.')

check_event_dates(df, 'date', 'event_date')


import pandas as pd

def check_exposure(df, exposure_column, collateral_column):
    # Check if the exposure is larger than the collateral
    exposure_larger_than_collateral = df[exposure_column] > df[collateral_column]
   
    # If there are any rows where the exposure is larger than the collateral, raise an error
    if exposure_larger_than_collateral.any():
        raise ValueError(f'There are {exposure_larger_than_collateral.sum()} rows where the exposure is larger than the collateral.')
    else:
        print('All rows have exposure less than or equal to the collateral.')

check_exposure(df, 'exposure', 'collateral')


