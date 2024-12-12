# Supply Chain Dashboard

## Overview
The Supply Chain Dashboard is a comprehensive web application built with Streamlit that provides real-time insights into supply chain operations. The dashboard offers multiple views and analyses for different components of the supply chain network.

## Key Components

### 1. Data Management
- Version control for supply chain schemas
- Timestamp-based data retrieval
- Real-time and archived data access

### 2. Interactive Visualizations
- Network graphs showing supply chain relationships
- Time series analysis of various metrics
- Interactive filters and selectors

### 3. Entity Analysis
- [Business Group](business_group.md): Revenue analysis and group relationships
- [Product Family](product_family.md): Product categorization and performance
- [Product Offering](product_offering.md): Individual product details and metrics
- [Warehouse](warehouse.md): Inventory management and distribution
- [Facility](facility.md): Manufacturing and production insights
- [Parts](parts.md): Component tracking and inventory
- [Supplier](supplier.md): Supplier relationships and performance

## Technical Architecture

### Backend Components
- Graph database for relationship management
- REST APIs for data retrieval
- Caching mechanisms for performance optimization

### Frontend Features
- Responsive Streamlit interface
- Interactive plotly visualizations
- NetworkX-based graph visualizations

## Supply Chain Query Algorithm

The supply chain query system implements a comprehensive algorithm to determine how to fulfill product demands. The algorithm follows these steps:

### Main Query Flow
1. Check warehouse availability for the requested product
2. If warehouse inventory is sufficient, return warehouse details
3. If warehouse inventory is insufficient:
   - Find manufacturing facilities
   - Calculate required raw materials
   - Check raw material availability
   - Identify suppliers for missing materials

### Subqueries

#### 1. Warehouse Inventory Check
- Function: `check_units_available_in_warehouse`
- Purpose: Determines if requested product units are available in warehouses
- Returns: Available units per warehouse and warehouse details (name, type, location, size)

#### 2. Manufacturing Facility Identification
- Function: `find_facilty_making_product`
- Purpose: Locates facilities capable of manufacturing the requested product
- Analyzes: FACILITYToPRODUCT_OFFERING relationships

#### 3. Raw Materials Analysis
- Function: `find_raw_materials_to_make_product`
- Purpose: Identifies required raw materials and their quantities,cost and the lead_time
- Tracks: Quantity, cost, and lead time for each material

#### 4. Cost and Time Calculation
- Function: `calulate_cost_and_time`
- Purpose: Computes total manufacturing cost and time
- Includes: 
  - Raw material costs
  - Facility operational costs
  - Production lead times

#### 5. Raw Material Availability
- Function: `check_warehouse_have_enough_raw_material`
- Purpose: Verifies if warehouses have sufficient raw materials
- Returns: Availability status and shortage quantities

#### 6. Supplier Identification
- Function: `get_supplier_for_raw_material`
- Purpose: Maps suppliers to required raw materials
- Returns: Supplier details including:
  - Location
  - Reliability rating
  - Size and category
  - Material supply capabilities

### Query Response Types
1. Type 1: Demand can be satisfied from warehouse inventory
2. Type 2: Manufacturing required with available raw materials
3. Type 3: Manufacturing required with supplier sourcing

## Network Analysis

### Centrality Analysis
The dashboard implements comprehensive network analysis using degree centrality metrics to understand the connectivity and importance of different nodes in the supply chain network.It displays the important nodes in each category , and any failure in that particular node would cause disruption in the supply chain.


#### Analysis Components
- Function: `count_connections_and_find_max_nodes`
- Purpose: Analyzes network connectivity and identifies key nodes
- Metrics tracked:
  - Outgoing connections
  - Incoming connections
  - Total degree centrality

#### Node Classification
Nodes are categorized into seven main groups:
1. Business Groups (BG_)
2. Product Families (PF_)
3. Product Offerings (PO_)
4. Facilities (F_)
5. Parts (P_)
6. Suppliers (S_)
7. Warehouses (W_)

#### Analysis Outputs
- Grouped node statistics
- Maximum connection nodes identification
- Centrality rankings per category


#### Display Components
- Function: `display_node_boxes`
- Layout: 2-2-3 column grid structure
- Node types displayed:
  - Business Group
  - Product Family
  - Product Offering
  - Facility
  - Parts
  - Suppliers
  - Warehouse

#### Visual Features
- Gradient background styling
- Hover effects
- Shadow effects
- Responsive layout
- Centralized text alignment

#### Style Characteristics
- Border radius: 5px
- Color scheme: Blue to purple gradient
- Box shadow: Subtle depth effect
- Interactive transitions
- Consistent padding and margins

### Graph Construction
- Function: `convert_json_to_graph`
- Purpose: Converts JSON data into a NetworkX directed graph
- Components:
  - Node attribute mapping
  - Edge relationship mapping
  - Relationship type preservation

### Schema Visualization
- Usage : It Embedds an html page which displays the complete schema of the supply chain network
- Interactive features:
  - Hover text
  - Node selection
  - Edge selection


## Performance Features
- Memory usage tracking
- Execution time monitoring
- Caching for frequently accessed data

## Dependencies
- Streamlit: Web application framework
- NetworkX: Graph operations and analysis
- Plotly: Interactive visualizations
- Matplotlib: Static visualizations
- Python-dotenv: Environment configuration
- Requests: API communication


## Future Enhancements
- Advanced analytics integration
- Machine learning predictions
- Additional visualization options
- Enhanced export capabilities
- Real-time alerts and notifications