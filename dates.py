import pandas as pd
from datetime import datetime

# Example datetimes
datetime1 = datetime(2023, 1, 1, 12, 0, 0)
datetime2 = datetime(2023, 1, 2, 15, 30, 0)

# Calculate the time difference
time_difference = datetime2 - datetime1

# Example DataFrame with a datetime column
df = pd.DataFrame({
    'timestamp': pd.date_range(start='2023-01-10', periods=5, freq='D')
})

# Add the time difference to the datetime column
df['new_timestamp'] = df['timestamp'] + time_difference

# Set the datetime display format while keeping the datetime dtype
pd.options.display.date_format = '%Y-%m-%d'

# Alternatively, if you need a string column with the format
df['formatted_date'] = df['new_timestamp'].dt.strftime('%Y-%m-%d')

print(df)
print("\nDtypes:")
print(df.dtypes)
