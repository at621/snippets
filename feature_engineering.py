import numpy as np
import pandas as pd

# suppose we have the following DataFrame
df = pd.DataFrame({
    'a': [1, 2, 3],
    'b': [4, 5, 6],
    'c': ['one', 'two', 'three'],
    'd': [7, 8, 9]
})

# define some custom functions
def square(x):
    return x ** 2, '_squared'

def string_length(x):
    return x.str.len(), '_length'  # this function works on a pandas Series of strings

# define a dictionary that maps dtype names to functions
operations = {
    'number': square,
    'object': string_length
}

# apply each function to the appropriate column
for dtype, function in operations.items():
    for col in df.select_dtypes(include=dtype).columns:
        new_data, suffix = function(df[col])
        df[col + suffix] = new_data

print(df)

# suppose we have the following DataFrame
df = pd.DataFrame({
    'a': [1, 2, 3],
    'b': [4, 5, 6],
    'c': ['one', 'two', 'three']
})

# define some custom functions
def square(x):
    return x ** 2

def add_ten(x):
    return x + 10

def string_length(x):
    return len(x)

# define a dictionary that maps variable names to functions
# note: you can store numpy functions directly without defining a custom function first
operations = {
    'a': square,
    'b': add_ten,
    'c': string_length
}

# apply each function to the appropriate column
for column, function in operations.items():
    df[column] = df[column].apply(function)

print(df)

