# Warehouse Page

## Overview

The Warehouse page of the dashboard provides comprehensive management and analysis of storage facilities within the supply chain network.According to design of our supply chain there are three types of warehouses: LAM warehouse , Subassembly warehouse and Supplier warehouse. And each warehouse has 3 differnet sizes: small, medium and large.

## Key Components

### Visualization and Analysis
- **Warehouse Distribution Overview**: Uses Plotly's scatter_mapbox to create an interactive geographical visualization of all warehouses. Each warehouse is represented on the map with its location data and color-coded based on its storage capacity and utilization.

Built with Plotly's mapping functions, this feature provides:
  - Interactive zoom and pan capabilities
  - Clickable warehouse markers with popup information
  - Custom map styling with mapbox
  - Warehouse clustering for dense regions
  - Color-coded capacity indicators

- **Warehouse Distribution based on the size**: Uses Plotly's bar chart to display the distribution of warehouse sizes.

Built with Plotly's bar chart functions, this feature provides:
  - Detailed breakdown of warehouse sizes
  - Interactive hover effects for data insights
  - Customizable color scheme for clarity

### Analysis Tools

1. Storage Management Analysis
   - **Warehouse Capacity Monitoring**: 
     - Function: `check_units_available_in_warehouse()`
     - Uses: NetworkX for data traversal, Pandas for capacity calculations 
     - Usage: Traverses the supply chain graph to check product availability  
     - Process: Tracks real-time inventory levels and available storage space
   
   - **Safety Stock Analysis**:
     - Function: `find_warehouses_below_safety_stock()`
     - Process: Identifies warehouses where stock levels are below safety thresholds (15% of max capacity)
     - Output: List of warehouses requiring attention

   - **Storage Cost Optimization**:
     - Function: `find_warehouses_by_storage_cost()`
     - Process: Analyzes and ranks warehouses based on storage costs
     - Output: DataFrame with cost-based warehouse rankings

2. Supply Chain Analysis
   - **Supplier Relationship Tracking**:
     - Function: `find_suppliers_to_warehouse_table()`
     - Process: Maps supplier connections and transportation costs
     - Usage: Traverses the supply chain graph to identify which supplier supplies what to a specific warehouse 
     - Output: Structured supplier relationship data

   - **Parts Inventory Analysis**:
     - Function: `find_parts_for_warehouse()`
     - Process: Detailed inventory tracking of parts in each warehouse
     - Output: Comprehensive parts inventory report

   - **Network Visualization**:
     - Function: `create_graph()`
     - Uses: NetworkX and Plotly for interactive visualization and it shows warehouse relationship within the supply chain
     - Process: Creates interactive supply chain network diagrams

## Core Functions

### Analysis Functions
- `check_units_available_in_warehouse()`: 
  - Input: Product ID and graph data
  - Process: Traverses warehouse inventory to check product availability
  - Output: Available units and warehouse locations

- `find_warehouses_below_safety_stock()`:
  - Input: Warehouse graph data
  - Process: Analyzes capacity utilization against safety thresholds (15% rule)
  - Output: List of warehouses below safety stock levels

- `find_warehouses_by_storage_cost()`:
  - Input: Warehouse data
  - Process: Ranks warehouses based on storage cost efficiency
  - Output: Sorted list of warehouses by cost metrics

### Supply Chain Management
- `find_suppliers_to_warehouse_table()`:
  - Input: Warehouse ID and graph data
  - Process: Analyzes supplier relationships and transportation routes
  - Output: Detailed supplier-warehouse relationship table

- `find_parts_for_warehouse()`:
  - Input: Warehouse ID
  - Process: Comprehensive inventory analysis of parts stored in the warehouse
  - Output: Structured parts inventory list

- `node_details()`:
  - Input: Warehouse ID and timestamp
  - Process: Gathers and displays comprehensive warehouse information including capacity, costs, and relationships
  - Output: Detailed warehouse metrics and visualizations

### Visualization Functions
- `create_warehouse_map()`:
  - Input: Warehouse location and capacity data
  - Process: Creates interactive geographical visualization of warehouse network
  - Output: Interactive Plotly mapbox visualization

- `donut_chart()`:
  - Input: Warehouse size distribution data
  - Process: Creates visual representation of warehouse capacity distribution
  - Output: Interactive donut chart showing size categories

## Dependencies
- **streamlit**: Main dashboard framework and UI components
- **plotly**: Interactive charts, maps, and network visualizations
- **networkx**: Graph operations and network analysis
- **altair**: Additional visualization capabilities
- **pandas**: Data manipulation and analysis
- **json**: Data structure handling
