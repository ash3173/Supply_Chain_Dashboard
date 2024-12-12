# Product Family Page

## Overview

The Product Family page of the dashboard provides comprehensive management and analysis of product families within the supply chain network. A product family represents a group of related products that share common characteristics or manufacturing processes. Each product family can contain multiple product offerings.

## Key Components

### Visualization and Analysis
- **Product Family Network Overview**: Uses Plotly's network visualization to create an interactive view of product family relationships.

Built with Plotly's network functions, this feature provides:
  - Interactive node selection
  - Relationship highlighting
  - Hierarchical layout visualization
  - Color-coded product categories
  - Drill-down capabilities to product offerings

- **Revenue Analysis**: Uses Plotly's time series charts to analyze revenue patterns.

Built with Plotly's charting functions, this feature provides:
  - Revenue trends over time
  - Comparative analysis between product families
  - Interactive tooltips with revenue details
  - Customizable time range selection

### Analysis Tools

1. Performance Analysis
   - **Revenue Tracking**: 
     - Function: `plot_revenues()`
     - Uses: Plotly for visualization, Pandas for data processing
     - Usage: Analyzes revenue patterns across different time periods
     - Process: Creates interactive revenue visualizations
   
   - **Product Family Relationships**:
     - Function: `create_graph()`
     - Process: Builds network visualization showing relationships between product families and their offerings
     - Usage: Helps understand product hierarchy and relationships
     - Output: Interactive network diagram

2. Product Management
   - **Node Details Analysis**:
     - Function: `node_details()`
     - Process: Displays detailed information about specific product families
     - Usage: Provides comprehensive view of product family attributes and relationships
     - Output: Structured product family information

## Core Functions

### Analysis Functions
- `plot_revenues()`: 
  - Input: Revenue data across time periods
  - Process: Creates time series visualizations of revenue patterns
  - Output: Interactive revenue charts

- `create_graph()`:
  - Input: Product family relationship data
  - Process: Constructs network visualization showing product family hierarchy
  - Output: Interactive network diagram showing product relationships

### Product Management Functions
- `node_details()`:
  - Input: Product family ID and timestamp
  - Process: Gathers and displays comprehensive product family information
  - Usage: Shows detailed metrics and relationships for selected product family
  - Output: Detailed product family metrics


### Data Processing Functions
- `static_part()`:
  - Input: Temporal graph data
  - Process: Initializes dashboard with basic visualizations
  - Output: Base dashboard components

## Dependencies
- **streamlit**: Main dashboard framework and UI components
- **plotly**: Interactive charts and network visualizations
- **networkx**: Graph operations and relationship analysis
- **pandas**: Data manipulation and analysis
- **json**: Data structure handling
