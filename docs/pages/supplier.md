# Supplier Dashboard
---

## Overview

The Supplier Dashboard application provides insights into supply chain data using a temporal graph. It includes functionalities for visualization, queries, and performance evaluation.

---

### Visualization

- *Static Part Visualization*: Displays node and edge schema.
- *Subgraph Visualization*: Provides detailed relationships of nodes using ego graphs.

---

## Query Functions

### 1. Supplier Reliability and Costing Analysis

Filters suppliers based on reliability thresholds and maximum transportation cost.

*Parameters:*
- reliability_threshold: Minimum acceptable reliability.
- max_transportation_cost: Maximum transportation cost.

### 2. Lead Time Query

Finds the lead time between a supplier and a warehouse.

*Parameters:*
- supplier_id: ID of the supplier.
- warehouse_id: ID of the warehouse.

### 3. Suppliers by Part Type

Identifies suppliers based on a specified part type.

*Parameters:*
- part_type: Type of part supplied by suppliers.

### 4. Unused Suppliers

Lists suppliers with no active edges in the graph.

### 5. Supplier-Product Offering Association

Analyzes product offerings associated with suppliers through their relationships with warehouses and facilities.

---

## Code Structure

### Utility Functions

*Graph Creation*: Generates a graphical representation of the node and edge schema.

*Visualization Functions:* Choropleth maps for supplier distribution. Bar charts for item frequency.

### Streamlit Fragments

- **node_details_input**: Collects user inputs to display node details.
- **queries**: Allows users to perform supplier-based queries.

### Main Function

The main entry point for the application. Includes sections for:

    - Static Part Visualization.
    - Node Details Input.
    - Query Execution.

---

## Usage Instructions

1. Run the script using Streamlit: streamlit run main.py.
2. Interact with the dashboard to explore supplier-related data.
3. Perform queries to retrieve specific insights.

---

## Performance Considerations

- Minimize complex queries on large graphs.
- Monitor memory usage with large datasets to avoid crashes.
---

## Dependencies

- Python Libraries: streamlit, json, plotly, pandas, networkx, requests
- *Version Requirements:* Ensure compatible versions of libraries are installed.


---

## Recommended Improvements

- Include advanced visualization options for better data exploration.
- Add export functionality for query results.
- Implement real-time data updates from external sources to improve insights.