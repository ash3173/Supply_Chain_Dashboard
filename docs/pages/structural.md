# Structural Dashboard

---

## Overview

The Structural Graph Dashboard provides an interface for exploring and analyzing relationships in a temporal graph. Users can visualize the structure of a graph and execute specific queries to extract insights about nodes, edges, and paths.

---

## Query Functions

### 1. Ego Graph

*Purpose:*
Visualize the subgraph around a selected node within a specified radius.

*Input:*

    - node_id: The ID of the node to center the ego graph.
    - radius: The number of hops from the node to include in the subgraph.

*Output:*
- A subgraph with details of nodes and edges within the radius.
- Plotly visualization of the subgraph.

*NetworkX Function:*
- nx.ego_graph()

### 2. Node Details

*Purpose:*
Retrieve attributes of a specific node in the graph.

*Input:*
- node_id: The ID of the node.

*Output:*
- A JSON object containing node attributes such as type, name, and additional metadata.

*NetworkX Function:*
- graph.nodes[node_id]

### 3. Edge Attributes

*Purpose:*
Retrieve attributes of all edges connected to a specific node.

*Input:*
- node_id: The ID of the node whose edges are being queried.

*Output:*
- A list of edges connected to the node, including their attributes.

*NetworkX Function:*

    - graph.neighbors(node_id)
    - graph.get_edge_data(node_id, neighbor)

### 4. Shortest Path

*Purpose:*
Find the shortest path between two nodes in the graph.

*Input:*

    - source: Source node ID.
    - destination: Destination node ID.

*Output:*

    - The path as a list of nodes.
    - The length of the path.
    - A Plotly visualization highlighting the path in the graph.

*NetworkX Functions:*

    - nx.shortest_path(graph, source=source, target=destination)
    - nx.shortest_path_length(graph, source=source, target=destination)

### 5. Ancestors and Descendants

*Purpose:*
Identify all ancestors and descendants of a specific node in a directed graph.

*Input:*
- node_id: The ID of the node.

*Output:*
- Two lists containing ancestors and descendants of the node.

*NetworkX Functions:*

    - nx.ancestors(graph, node_id)
    - nx.descendants(graph, node_id)

---

## Visualization

- *Graph Schema*: Visualizes the overall graph layout.
- *Ego Graphs*: Focused subgraphs around specific nodes.
- *Path Visualization*: Highlights the shortest path between two nodes.

---

## Code Structure

### Utility Functions

- *Graph Querying*:
  - ego_graph_query: Extracts the ego graph for a node.
  - node_details_query: Retrieves attributes of a node.
  - retrieve_edge_attributes: Retrieves edge details for a node.
  - find_shortest_path: Computes the shortest path between nodes.
  - get_ancestors_descendants: Identifies ancestors and descendants of a node.

### Streamlit Integration

- Dropdowns and sliders for user input.
- Visualization of query results using Plotly.

---

## Usage Instructions

1. Run the script using Streamlit: streamlit run 8_Structural.py.
2. Select a query type from the dropdown menu.
3. Provide the required inputs for the query.
4. View the results and visualizations directly on the dashboard.

---

## Dependencies

- Python Libraries: streamlit, networkx, plotly, numpy
- *Version Requirements:* Ensure compatible library versions.

---

## Recommended Improvements

- Expand visualization options for complex graph relationships.
- Incorporate support for live graph updates from external sources.
- Implement advanced analytics like centrality and clustering coefficient calculations.