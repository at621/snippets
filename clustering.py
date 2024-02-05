import pandas as pd
import numpy as np
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
from scipy.spatial.distance import squareform
from sklearn.metrics import silhouette_score
from scipy.stats import pearsonr, spearmanr

# Function to calculate distance based on correlation
def correlation_distance(df, method='pearson'):
    if method == 'pearson':
        corr = df.corr(method='pearson')
    elif method == 'spearman':
        corr = df.corr(method='spearman')
    # Convert correlation to distance
    dist = 1 - corr
    return dist

# Function for hierarchical clustering and determining the number of clusters
def hierarchical_clustering(df, metric='raw pearson', k=None):
    # Calculate distance matrix
    dist = correlation_distance(df, metric.split()[1])
    # Convert to condensed distance matrix for linkage method
    condensed_dist = squareform(dist, checks=False)
    # Perform hierarchical clustering
    Z = linkage(condensed_dist, 'average')
    
    # Determine the optimal number of clusters if not specified
    if k is None:
        # Use silhouette score to find the optimal number of clusters, k
        range_n_clusters = list(range(2, min(len(df.columns), 10) + 1))
        best_score = -1
        for n_clusters in range_n_clusters:
            labels = fcluster(Z, n_clusters, criterion='maxclust')
            score = silhouette_score(squareform(condensed_dist), labels, metric='precomputed')
            if score > best_score:
                best_score = score
                k = n_clusters
                
    # Assign clusters
    clusters = fcluster(Z, k, criterion='maxclust')
    
    # Create a DataFrame with risk factors and their assigned clusters
    cluster_df = pd.DataFrame({'Risk Factor': df.columns, 'Cluster': clusters})
    
    return cluster_df

# Dummy data
np.random.seed(42)  # For reproducible results
data = np.random.rand(100, 5)  # 100 observations of 5 risk factors
df = pd.DataFrame(data, columns=['Risk Factor 1', 'Risk Factor 2', 'Risk Factor 3', 'Risk Factor 4', 'Risk Factor 5'])

# Apply the hierarchical clustering function
cluster_results = hierarchical_clustering(df, metric='raw pearson', k=None)
cluster_results
