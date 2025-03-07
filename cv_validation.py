import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.formula.api import ols
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import statsmodels.api as sm
from patsy import dmatrix, dmatrices
import warnings
warnings.filterwarnings('ignore')

# Set seed for reproducibility
np.random.seed(42)

# Generate sample time series data
def generate_time_series_data(n_samples=500):
    """Generate synthetic time series data with trend, seasonality, and noise"""
    
    # Time index
    date_rng = pd.date_range(start='2018-01-01', periods=n_samples, freq='D')
    
    # Time features
    t = np.arange(n_samples)
    trend = 0.01 * t
    seasonality = 2 * np.sin(2 * np.pi * t / 365.25)  # Annual cycle
    weekly = 0.5 * np.sin(2 * np.pi * t / 7)  # Weekly cycle
    
    # Create some features (predictors)
    x1 = np.random.normal(0, 1, n_samples)
    x2 = 0.5 * np.sin(t / 50) + 0.1 * np.random.normal(0, 1, n_samples)
    x3 = 0.3 * np.cos(t / 30) + 0.05 * np.random.normal(0, 1, n_samples)
    
    # Generate the target variable with noise
    y = 2 + 0.5 * x1 + 1.5 * x2 + 0.8 * x3 + trend + seasonality + weekly + 0.5 * np.random.normal(0, 1, n_samples)
    
    # Create a DataFrame
    df = pd.DataFrame({
        'date': date_rng,
        'y': y,
        'x1': x1,
        'x2': x2,
        'x3': x3,
        'time': t,
        'month': [d.month for d in date_rng],
        'day_of_week': [d.dayofweek for d in date_rng]
    })
    
    # Add cyclical features for month and day of week (better than categorical for time series)
    df['month_sin'] = np.sin(2 * np.pi * df['month']/12)
    df['month_cos'] = np.cos(2 * np.pi * df['month']/12)
    df['dow_sin'] = np.sin(2 * np.pi * df['day_of_week']/7)
    df['dow_cos'] = np.cos(2 * np.pi * df['day_of_week']/7)
    
    df = df.set_index('date')
    return df

# Time series cross-validation function
def time_series_cv(df, formula, n_splits=5, min_train_size=0.5, test_size=0.2):
    """
    Perform time series cross-validation with expanding window.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        Time series data with datetime index
    formula : str
        Formula for statsmodels OLS
    n_splits : int
        Number of validation splits
    min_train_size : float
        Minimum fraction of data to use for initial training
    test_size : float
        Fraction of data to use for each test set
    
    Returns:
    --------
    dict
        Dictionary containing train/test indices, predictions, and metrics
    """
    n = len(df)
    min_train_samples = int(n * min_train_size)
    test_samples = int(n * test_size)
    
    # Initialize results
    results = {
        'train_indices': [],
        'test_indices': [],
        'predictions': [],
        'actuals': [],
        'residuals': [],
        'mse': [],
        'mae': [],
        'r2': [],
        'coefficients': [],
        'models': []
    }
    
    # Create split indices
    for i in range(n_splits):
        if i == 0:
            # First split uses minimum training size
            train_end = min_train_samples
        else:
            # Subsequent splits expand the training window
            train_end = min_train_samples + i * ((n - min_train_samples - test_samples) // (n_splits - 1))
        
        test_start = train_end
        test_end = min(test_start + test_samples, n)
        
        if test_end <= test_start:
            continue
            
        # Extract train and test sets
        train_indices = list(range(0, train_end))
        test_indices = list(range(test_start, test_end))
        
        train_df = df.iloc[train_indices].copy()
        test_df = df.iloc[test_indices].copy()
        
        # Fit OLS model
        model = ols(formula=formula, data=train_df).fit()
        
        # Create design matrix for prediction using patsy - safer for time series
        try:
            # Method 1: Try standard predict with dataframe
            predictions = model.predict(test_df)
        except Exception:
            # Method 2: Manually create design matrix when method 1 fails
            # Get the exog variable names
            exog_names = model.model.exog_names
            # Get design matrix from test_df
            X_test = dmatrix(formula.split('~')[1], data=test_df)
            # Convert to DataFrame
            X_test_df = pd.DataFrame(X_test, columns=X_test.design_info.column_names)
            # Reorder columns to match model's exog_names (excluding Intercept)
            X_test_df = X_test_df[exog_names[1:]]
            # Add intercept
            X_test_df.insert(0, 'Intercept', 1.0)
            # Now predict
            predictions = model.predict(X_test_df)
        
        actuals = test_df['y']
        residuals = actuals - predictions
        
        # Calculate metrics
        mse = mean_squared_error(actuals, predictions)
        mae = mean_absolute_error(actuals, predictions)
        r2 = r2_score(actuals, predictions)
        
        # Store results
        results['train_indices'].append(train_indices)
        results['test_indices'].append(test_indices)
        results['predictions'].append(predictions)
        results['actuals'].append(actuals)
        results['residuals'].append(residuals)
        results['mse'].append(mse)
        results['mae'].append(mae)
        results['r2'].append(r2)
        results['coefficients'].append(model.params)
        results['models'].append(model)
        
    return results

# Visualize cross-validation results
def plot_cv_results(df, cv_results, n_splits):
    """Plot cross-validation results"""
    
    # Create a figure with subplots
    fig = plt.figure(figsize=(15, 15))
    
    # 1. Plot the original time series
    ax1 = plt.subplot2grid((3, 2), (0, 0), colspan=2)
    ax1.plot(df.index, df['y'], label='Original Time Series')
    ax1.set_title('Original Time Series Data')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Value')
    ax1.legend()
    
    # 2. Plot predictions vs actuals for each fold
    ax2 = plt.subplot2grid((3, 2), (1, 0), colspan=2)
    
    colors = plt.cm.viridis(np.linspace(0, 1, n_splits))
    
    for i in range(len(cv_results['test_indices'])):
        test_indices = cv_results['test_indices'][i]
        predictions = cv_results['predictions'][i]
        actuals = cv_results['actuals'][i]
        
        test_dates = df.index[test_indices]
        
        ax2.plot(test_dates, actuals, 'o-', color=colors[i], alpha=0.7, label=f'Actual (Fold {i+1})')
        ax2.plot(test_dates, predictions, 's--', color=colors[i], alpha=0.7, label=f'Predicted (Fold {i+1})')
    
    ax2.set_title('Actual vs Predicted Values Across CV Folds')
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Value')
    ax2.legend(loc='upper left', bbox_to_anchor=(1.05, 1), borderaxespad=0.)
    
    # 3. Plot MSE, MAE, and R² for each fold
    ax3 = plt.subplot2grid((3, 2), (2, 0))
    fold_nums = range(1, len(cv_results['mse']) + 1)
    
    ax3.plot(fold_nums, cv_results['mse'], 'o-', label='MSE')
    ax3.plot(fold_nums, cv_results['mae'], 's-', label='MAE')
    ax3.set_title('Error Metrics Across CV Folds')
    ax3.set_xlabel('Fold Number')
    ax3.set_ylabel('Error Value')
    ax3.set_xticks(fold_nums)
    ax3.legend()
    
    ax4 = plt.subplot2grid((3, 2), (2, 1))
    ax4.plot(fold_nums, cv_results['r2'], 'o-', label='R²', color='green')
    ax4.set_title('R² Across CV Folds')
    ax4.set_xlabel('Fold Number')
    ax4.set_ylabel('R² Value')
    ax4.set_xticks(fold_nums)
    ax4.legend()
    
    plt.tight_layout()
    plt.show()
    
    # Plot coefficient evolution
    plt.figure(figsize=(12, 6))
    coef_df = pd.DataFrame([cv_results['coefficients'][i] for i in range(len(cv_results['coefficients']))])
    
    for column in coef_df.columns:
        plt.plot(fold_nums, coef_df[column], 'o-', label=column)
    
    plt.title('Coefficient Evolution Across CV Folds')
    plt.xlabel('Fold Number')
    plt.ylabel('Coefficient Value')
    plt.xticks(fold_nums)
    plt.legend(loc='upper left', bbox_to_anchor=(1.05, 1), borderaxespad=0.)
    plt.tight_layout()
    plt.show()
    
    # Plot residuals
    plt.figure(figsize=(12, 4))
    for i in range(len(cv_results['residuals'])):
        test_indices = cv_results['test_indices'][i]
        residuals = cv_results['residuals'][i]
        test_dates = df.index[test_indices]
        plt.scatter(test_dates, residuals, label=f'Fold {i+1}', alpha=0.7)
    
    plt.axhline(y=0, color='r', linestyle='-')
    plt.title('Residuals Across CV Folds')
    plt.xlabel('Date')
    plt.ylabel('Residual')
    plt.legend(loc='upper left', bbox_to_anchor=(1.05, 1), borderaxespad=0.)
    plt.tight_layout()
    plt.show()

# Main execution
if __name__ == "__main__":
    # Generate sample data
    print("Generating sample time series data...")
    df = generate_time_series_data(n_samples=500)
    
    # Display data summary
    print("\nData Summary:")
    print(df.head())
    print("\nShape:", df.shape)
    print("\nDescriptive Statistics:")
    print(df.describe())
    
    # Define the formula for the OLS model - using cyclical features instead of categorical
    formula = 'y ~ x1 + x2 + x3 + month_sin + month_cos + dow_sin + dow_cos'
    
    # Perform time series cross-validation
    print("\nPerforming time series cross-validation...")
    cv_results = time_series_cv(df, formula, n_splits=5, min_train_size=0.5, test_size=0.1)
    
    # Display cross-validation results
    print("\nCross-Validation Results:")
    for i in range(len(cv_results['mse'])):
        print(f"Fold {i+1}:")
        print(f"  MSE: {cv_results['mse'][i]:.4f}")
        print(f"  MAE: {cv_results['mae'][i]:.4f}")
        print(f"  R²: {cv_results['r2'][i]:.4f}")
    
    # Average metrics
    avg_mse = np.mean(cv_results['mse'])
    avg_mae = np.mean(cv_results['mae'])
    avg_r2 = np.mean(cv_results['r2'])
    
    print("\nAverage Performance:")
    print(f"  MSE: {avg_mse:.4f}")
    print(f"  MAE: {avg_mae:.4f}")
    print(f"  R²: {avg_r2:.4f}")
    
    # Print final model summary (from the last fold)
    print("\nFinal Model Summary (Last Fold):")
    print(cv_results['models'][-1].summary())
    
    # Plot cross-validation results
    plot_cv_results(df, cv_results, len(cv_results['mse']))

    print("\nAnalysis complete!")

    # Example of how to use with a real dataset (commented out)
    """
    # Load your real time series data
    # df = pd.read_csv('your_data.csv', parse_dates=['date_column'], index_col='date_column')
    
    # Define your formula based on your predictors
    # formula = 'target ~ predictor1 + predictor2 + ... + C(categorical_var)'
    
    # Run the cross-validation
    # cv_results = time_series_cv(df, formula, n_splits=5, min_train_size=0.6, test_size=0.1)
    
    # Visualize the results
    # plot_cv_results(df, cv_results, len(cv_results['mse']))
    """
