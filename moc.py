import pandas as pd
import numpy as np

def calculate_moc_c(df: pd.DataFrame, column_name: str) -> float:
    """
    Calculate MoC C based on a series of annual default rates.

    Parameters:
    df (pd.DataFrame): DataFrame containing the annual default rates.
    column_name (str): The name of the column containing the annual default rates in the DataFrame.

    Returns:
    float: The calculated MoC C value.
    float: The calculated Average Standard Deviation.

    Example:
    >>> df = pd.DataFrame({'Year': [2010, 2011, 2012, 2013, 2014, 2015],
                           'Default_Rate': [0.05, 0.04, 0.06, 0.03, 0.07, 0.05]})
    >>> calculate_moc_c(df, 'Default_Rate')
    """
    # Validate if the column exists in the DataFrame
    if column_name not in df.columns:
        raise ValueError(f"Column '{column_name}' not found in DataFrame.")

    # Calculate Standard Deviation of the Mean of Annual Defaults
    std_dev_mean = np.std(df[column_name]) / np.sqrt(len(df))

    # Calculate Average Default Rate
    avg_default_rate = np.mean(df[column_name])

    # Calculate MoC C
    moc_c = std_dev_mean / avg_default_rate

    return moc_c, std_dev_mean

# Example usage
df = pd.DataFrame({
    'Year': [2010, 2011, 2012, 2013, 2014, 2015],
    'Default_Rate': [0.05, 0.04, 0.06, 0.03, 0.07, 0.05]
})

moc_c, avg_std_dev = calculate_moc_c(df, 'Default_Rate')
print(f"MoC C: {moc_c}")
print(f"Average Standard Deviation: {avg_std_dev}")
