from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.base import BaseEstimator, TransformerMixin
from scipy.stats.mstats import winsorize
import numpy as np

class Winsorizer(BaseEstimator, TransformerMixin):
    def __init__(self, limits=(0.05, 0.05)):
        self.limits = limits

    def fit(self, X, y=None):
        self.min_ = np.percentile(X, 100 * self.limits[0])
        self.max_ = np.percentile(X, 100 * (1 - self.limits[1]))
        return self

    def transform(self, X, y=None):
        return np.clip(X, self.min_, self.max_)

# Define imputation transformations for different columns
mean_imputer = SimpleImputer(strategy='mean')
median_imputer = SimpleImputer(strategy='median')
constant_imputer = SimpleImputer(strategy='constant', fill_value='missing')

# Specify the columns to which each imputer will be applied
mean_cols = ['col1', 'col2']
median_cols = ['col3', 'col4']
constant_cols = ['col5', 'col6']

# Define the winsorizer
winsorizer = Winsorizer(limits=(0.05, 0.05))
winsorize_cols = ['col1', 'col2', 'col3', 'col4']

# Define the column transformer
transformer = ColumnTransformer(transformers=[
    ('mean_imputer', mean_imputer, mean_cols),
    ('median_imputer', median_imputer, median_cols),
    ('constant_imputer', constant_imputer, constant_cols),
    ('winsorizer', winsorizer, winsorize_cols)
])

# Fit the transformer to the development dataset
transformer.fit(development_dataset)

# Transform both the development and test datasets
development_dataset = transformer.transform(development_dataset)
test_dataset = transformer.transform(test_dataset)



# Here's a brief comparison:
# float16 or Half-precision floating-point: This format uses 16 bits, with 1 bit for the sign of the number, 
# 5 bits for the exponent, and 10 bits for the fraction. It can represent numbers approximately between 
# 0.0000000596 and 65504 with some level of precision, but the level of precision decreases as the absolute 
# value of the number increases. The precision can get as low as 3-4 decimal places for larger values. 
# It's mainly used in scenarios where the range of values is not large, and precision is not of utmost concern, 
# but memory is a constraint.

# float32 or Single-precision floating-point: This format uses 32 bits, with 1 bit for the sign, 8 bits for the exponent, 
# and 23 bits for the fraction. It can represent a wider range of values approximately between 1.4E-45 and 3.4E+38 with 
# much greater precision than float16. The precision can be up to 7 decimal places. 
# It's a good balance between memory usage and precision for many applications.

# float64 or Double-precision floating-point: This format uses 64 bits, with 1 bit for the sign, 11 bits for the 
# exponent, and 52 bits for the fraction. It can represent a much larger range of values approximately between 
# 5E-324 and 1.8E+308 with even greater precision than float32. The precision can be up to 15-17 decimal places. 
# It's used in scenarios where high precision is required.
  
# convert float64 to float32
for col in df.select_dtypes(include='float64').columns:
    df[col] = df[col].astype(np.float32)

# convert object to categorical if possible
for col in df.select_dtypes(include='object').columns:
    try:
        df[col] = df[col].astype('category')
    except ValueError:  # in case conversion to category is not possible
        pass

# convert object to datetime if possible
date_cols = [...]  # replace this with the list of date columns names
for col in date_cols:
    df[col] = pd.to_datetime(df[col], errors='coerce')
  
  
