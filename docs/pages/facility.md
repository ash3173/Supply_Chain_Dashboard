# Facility Page

## Overview

The Facility page of the dashboard provides comprehensive management and analysis of manufacturing facilities within the supply chain network.

## Key Components

### Visualization and Analysis
- **Facility Distribution Overview**: Uses Plotly's scatter_mapbox to create an interactive geographical visualization of all facilities. Each facility is represented as a point on the map with its location data (latitude, longitude) and color-coded based on its operating cost.

Built with Plotly's mapping functions, this feature provides:
  - Interactive zoom and pan capabilities
  - Clickable facility markers with popup information
  - Custom map styling with mapbox
  - Facility clustering for dense regions


- **Operating Cost Analysis**: Implements pandas DataFrame operations to calculate and compare operating costs across facilities. The analysis includes mean, median, and quartile calculations to identify cost outliers and trends.
Uses Plotly Express to create:
  - Bar charts comparing costs across facilities
  - Time series plots showing cost trends
  - Box plots for cost distribution analysis
  - Interactive tooltips with detailed cost breakdowns


- **Production Capacity Tracking**: Utilizes NetworkX to analyze the production network and track capacity utilization. The system monitors real-time production loads against maximum capacity.
Combines Streamlit metrics and Plotly charts to display:
  - Real-time production rates
  - Capacity utilization percentages
  - Efficiency trends over time
  - Comparative analysis between similar facilities


### Analysis Tools

1. Operating Cost Analysis
   - **Average Operating Cost Computation**: 
     - Function: `compute_average_operating_costs()`
     - Uses: Pandas for data manipulation, NumPy for statistical calculations
     - Process: Aggregates cost data across timestamps and computes rolling averages
   
   - **Cost Comparison Between Facilities**:
     - Function: `plot_average_operating_cost()`
     - Uses: Plotly for visualization, Pandas for data preparation

   - **Threshold-based Analysis**:
     - Function: `find_product_offerings_under_threshold()`
     - Process: Identifies facilities operating below cost thresholds
     - Output: DataFrame with filtered facilities and their metrics

2. Production Analysis
   - **Product Offering Tracking**:
     - Uses NetworkX to trace product-facility relationships
     - Identifies bottlenecks and optimization opportunities

   - **Parts Requirement Analysis**:
     - Function: `find_all_parts_required_in_facility()`
     - Process: Traverses the supply chain graph to identify all required parts
     - Output: Structured list of parts with quantities and suppliers

   - **Production Capacity Monitoring**:
     - Real-time monitoring using Streamlit's metrics
     - Historical trend analysis with Plotly timelines
     - Predictive capacity planning capabilities


## Core Functions

### Analysis Functions
- `create_facility_map()`: 
  - Input: Facility node data with locations
  - Process: Creates interactive map using Plotly showing concentration of facilities in different states
  - Output: Mapbox figure with facility markers

- `compute_average_operating_costs()`:
  - Input: Facility cost data
  - Process: Statistical analysis using Pandas 
  - Output: Aggregated cost metrics

- `plot_average_operating_cost()`:
  - Input: Cost data for two facilities
  - Process: Comparative analysis and visualization
  - Output: Interactive Plotly comparison chart

- `find_product_offerings_under_threshold()`:
  - Input: Facility data and cost threshold
  - Process: Filtering and analysis
  - Output: List of qualifying facilities

### Production Management
- `find_all_parts_required_in_facility()`:
  - Input: Facility ID
  - Process: Graph traversal for parts identification.This function traverses the supply chain graph to identify all parts required by a specific facility.
  - Output: Structured parts requirement list

- `find_facilty_making_product()`:
  - Input: Product ID
  - Process: Reverse lookup in facility-product graph. This function identifies the facilities that produce a specific product.
  - Output: List of producing facilities

- `node_details()`:
  - Input: Facility ID and timestamp
  - Process: Comprehensive data gathering and displays the data associated with a specific facility and the relationships it has with other entities in the supply chain.
  - Output: Detailed facility information

### Network Visualization
- `create_graph()`: 
  - Input: Facility and relationship data
  - Process: NetworkX graph construction
  - Output: Interactive network showing supply chain relationships associated with a facility

## Dependencies
- **streamlit**: Main dashboard framework and UI components
- **plotly**: Interactive charts, maps, and network visualizations
- **networkx**: Graph operations and network analysis
- **matplotlib**: Additional static visualizations
- **pandas**: Data manipulation and analysis
- **requests**: API interactions and data fetching
