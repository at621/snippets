# Create a Pandas DataFrame with pairs of connected IDs.
# Use NetworkX to create a graph from these pairs.
# Find the connected components using NetworkX.

import pandas as pd
import networkx as nx

# Create a Pandas DataFrame with ID pairs
data = [("1", "2"), ("2", "3"), ("4", "5"), ("6", "7"), ("7", "8"), ("3", "6"), ("5", "9")]
columns = ["id1", "id2"]
df = pd.DataFrame(data, columns=columns)

# Create a NetworkX graph
G = nx.Graph()
for index, row in df.iterrows():
    G.add_edge(row["id1"], row["id2"])

# Find connected components
connected_components = list(nx.connected_components(G))

# Print connected components
for component in connected_components:
    print(component)
