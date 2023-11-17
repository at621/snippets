import numpy as np
from scipy.stats import norm

def inverse_matrix(transition_matrix):
    """
    Calculate the inverse matrix for a given transition matrix.

    The function iterates through each element of the transition matrix and fills
    the inverse matrix with values calculated using the normal cumulative distribution function (CDF).
    The CDF is applied to the sum of probabilities from the current state to the end.

    Parameters:
    transition_matrix (numpy.ndarray): A 2D array representing the transition matrix.

    Returns:
    numpy.ndarray: The inverse matrix corresponding to the input transition matrix.
    """
    # Initialize an empty matrix of the same shape as the transition matrix
    inverse_matrix = np.zeros(transition_matrix.shape)

    # Iterate through the transition matrix and calculate the inverse values
    for i, row in enumerate(transition_matrix):
        for j, _ in enumerate(row):
            cumulative_prob = np.sum(transition_matrix[i, j:], axis=0)
            # Ensure the cumulative probability is at most 1
            inverse_matrix[i, j] = norm.ppf(min(1, cumulative_prob))

    return inverse_matrix

def generate_pit_matrix(inverse_ttc, rho, z_score):
    """
    Generate a Point-in-Time (PIT) transition matrix based on an inverse TTC matrix,
    a correlation coefficient, and a Z-score.

    The PIT matrix is calculated by adjusting the inverse TTC matrix using the
    provided correlation coefficient (rho) and Z-score.

    Parameters:
    inverse_ttc (numpy.ndarray): An inverse Through-the-Cycle (TTC) matrix.
    rho (float): Correlation coefficient.
    z_score (float): Z-score from a normal distribution.

    Returns:
    numpy.ndarray: The Point-in-Time (PIT) transition matrix.
    """
    pit_matrix = np.zeros(inverse_ttc.shape)

    # Iterate through the inverse TTC matrix to fill the PIT matrix
    for i, row in enumerate(inverse_ttc):
        for j, _ in enumerate(row):
            if j < inverse_ttc.shape[1] - 1:
                adjusted_value = (inverse_ttc[i, j] - rho * z_score) / np.sqrt(1 - rho**2)
                next_adjusted_value = (inverse_ttc[i, j+1] - rho * z_score) / np.sqrt(1 - rho**2)
                pit_matrix[i, j] = norm.cdf(adjusted_value) - norm.cdf(next_adjusted_value)

        # Adjust the last column to ensure row sums to 1
        pit_matrix[i, -1] = 1 - np.sum(pit_matrix[i, :-1])

    return pit_matrix

# Example usage of the functions
ttc_matrix = np.array([[0.89, 0.01, 0.05, 0.05], [0.1, 0.6, 0.1, 0.2], [0.1, 0.2, 0.4, 0.3]])
print(f"Initial Through-the-Cycle (TTC) matrix:\n{ttc_matrix}\n")

inverse_ttc = inverse_matrix(ttc_matrix)
print(f"Inverse TTC matrix:\n{inverse_ttc}\n")

final_matrix = generate_pit_matrix(inverse_ttc, 0.05, 1)
print(f"Macro-adjusted Point-in-Time (PIT) matrix:\n{final_matrix}\n")

# Validate that all rows in the final matrix sum to 1
row_sums = final_matrix.sum(axis=1)
row_sums
