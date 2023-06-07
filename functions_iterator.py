import inspect

# Function definitions with annotations indicating the parameters they use
def func1(a: 'param', b: 'param'):
    return a + b

def func2(a: 'param', b: 'param', c: 'param'):
    return a * b - c

def func3(a: 'param'):
    return a**2

# Dictionary of functions
func_dict = {
    'add': func1,
    'subtract': func2,
    'square': func3,
}

# Define a dictionary of available parameters
params = {
    'a': 1,
    'b': 2,
    'c': 3,
    'd': 4,
}

# Loop over each function
for func_key, function in func_dict.items():
    # Get the list of parameter names that the function expects
    expected_params = list(inspect.signature(function).parameters.keys())
    
    # Select the required parameters from the available ones
    func_params = {k: params[k] for k in expected_params if k in params}

    # Execute the chosen function with the given parameters
    result = function(**func_params)

    print(f"Result of {func_key} with params {func_params} is: {result}")
