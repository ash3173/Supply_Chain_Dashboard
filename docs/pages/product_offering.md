# Product Offering Dashboard
## Overview

The Product Offering page of the dashboard provides comprehensive management and analysis of individual product offerings within the supply chain network. Product offerings are specific products that belong to product families, each with its own demand, cost, and performance metrics.

---

## Query Functions

### 1. Profitable Products Query

Identifies products that meet cost and demand thresholds.

*Parameters:*

    -  timestamp: Timestamp to query.
    -  cost_threshold: Maximum acceptable cost.
    -  demand_threshold: Minimum acceptable demand.

### 2. Cost and Demand Across Timestamps

Analyzes cost and demand trends for a specific product across timestamps.

*Parameters:*

    - product_offering_id: ID of the product offering.

### 3. Storage Cost Analysis

Examines storage costs for a product across different warehouses.

*Parameters:*

    - product_offering_id: ID of the product offering.
    - timestamp: Timestamp for analysis.

---

## Visualization

- *Static Schema Visualization*: Displays node and edge relationships.
- *Time-Series Analysis*:
    - Average Cost and Demand for Product Families.
    - Top Products by Demand.
- *Graph-Based Analysis*:
    - Ego graphs for node-specific relationships.

---

## Code Structure

### Utility Functions

- *Graph Creation*: Defines node and edge schema for visualization.
- *Data Retrieval*: Extracts nodes and edges based on query conditions.
- *Query Execution*:
      - Profitable products identification.
      - Cost and demand trends analysis.
      - Storage cost breakdown.

### Streamlit Fragments

- *Node Details Input*: Interactive input for node details.
- *Queries*: Execution of user-selected queries.

### Main Function

The primary function integrates all components:

  - Visualizes static schema and top products.
  - Handles node-specific details.
  - Processes user-defined queries.

---

## Usage Instructions

1. Run the script using Streamlit: streamlit run main.py.
2. Select a timestamp and product offering for exploration.
3. Visualize trends and execute queries for insights.

---

## Performance Considerations
  
- Ensure efficient memory usage by preprocessing data.
- Monitor browser performance for rendering complex visualizations.

---

## Dependencies

- Python Libraries: streamlit, requests, pandas, plotly, networkx, matplotlib
- *Version Requirements*: Ensure compatible library versions.
- *Hardware Requirements*: Minimum 8GB RAM for processing large temporal graphs.

---

## Recommended Improvements

- Enhance query functions for advanced analysis (e.g., profitability trends over time).
- Implement dynamic schema updates based on graph changes.
- Add real-time data ingestion for live monitoring.
- Expand visualization capabilities with 3D graph views.