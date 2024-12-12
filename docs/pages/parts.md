# Parts Dashboard

## Overview
The Parts Dashboard is a Streamlit-based application designed for interactive temporal graph exploration and parts inventory management. This application allows users to dynamically explore and analyze parts data across different timestamps.

---

## Data Exploration and Visualization

### *Static Part Visualization*
The static_part() function generates initial dashboard visualizations:
- Network graph representation
- Raw materials bar chart
- Subassembly materials bar chart
- Material type distribution donut chart

### *Node Details Input*
The node_details_input() function provides:
- Timestamp-based part selection
- Detailed part information display
- Neighboring nodes visualization
- Exploration of specific part data through drop-down menus
- Retrieval of node attributes from the session state and timestamped graph data
- Display of attributes in a styled table format for easy interpretation

### *Subgraph Visualization*
- Graph-based visualizations reveal relationships between entities, focusing on neighborhoods of selected nodes.
- Uses NetworkX’s ego_graph function to extract nodes within a defined radius.
- Visualizes the graph with Plotly, making attributes accessible through hover effects.

---

## Query Functions

### *1. Valid Parts Query*
*Function*: query_valid_parts_nx()  
- Identifies parts valid within a specific date range.
- Filters parts based on their valid_from and valid_till dates.

### *2. Most Common Subtypes Query*
*Function*: query_most_common_subtypes_nx()  
- Determines the most frequently occurring part subtypes.
- Uses Counter to calculate subtype frequencies.

### *3. Bottleneck Parts Analysis*
*Function*: bottleneck_parts_temporal()  
- Identifies potential bottleneck parts.
- Considers importance factor and lifecycle duration.

### *4. Suppliers for Part Query*
*Function*: query_suppliers_for_part_via_warehouse()  
- Traces suppliers for a specific part.
- Traverses graph connections: Part → Warehouse → Supplier.

### *5. Parts with Distance and Cost Analysis*
*Function*: parts_with_larger_distances_and_lower_costs()  
- Finds parts with significant transport distances.
- Analyzes transport costs and distances.

---

## Code Structure

### *Utility Functions*
- **time_and_memory_streamlit**: Tracks the execution time and memory usage of a function. Useful for performance profiling and optimization.
- **create_graph**: Generates a static visualization of the parts schema, including nodes representing warehouses, facilities, and parts. Uses Plotly to create an interactive graph.
- **query_valid_parts_nx**: Retrieves parts valid within a specified date range by filtering nodes based on their attributes.
- **query_most_common_subtypes_nx**: Identifies the most common part subtypes at a given timestamp, returning the top N.
- **bottleneck_parts_temporal**: Filters parts based on importance factors and lifespan to identify potential bottlenecks.
- **query_suppliers_for_part_via_warehouse**: Retrieves suppliers for a given part by traversing the graph.
- **parts_with_larger_distances_and_lower_costs**: Filters parts with significant transport distances but lower associated costs.

### *Streamlit Fragments*
- **static_part**:
  - Loads graph data for a specific timestamp.
  - Calculates raw material and subassembly distributions.
  - Creates multiple Plotly charts:
    - Network graph of the parts schema
    - Bar charts for material distributions
    - A donut chart for material types
- **node_details_input**:
  - Allows timestamp and part ID selection.
- **node_details**:
  - Fetches and displays detailed part information and attributes.

### *Main Function*
- Sets up the Streamlit application.
- Defines the layout and structure of the dashboard.
- Integrates utility functions and Streamlit fragments to create an interactive user interface.
- Handles user interactions and displays results dynamically.

---

## Usage Instructions

1. *Run the application*: Execute the main() function to start the Streamlit app.
2. *Select a timestamp*: Choose a specific point in time to analyze the graph.
3. *Explore static visualizations*: View the parts schema, material distribution, and other charts.
4. *Query node details*: Input a part ID to see its attributes and neighbors.
5. *Use query functionalities*: Perform queries such as finding valid parts, common subtypes, bottlenecks, suppliers, and parts with specific distance-cost relationships.

---

## Performance Considerations
- Tracks memory and time usage for key functions.
- Supports large temporal graph datasets.
- Responsive design with an adaptable layout.

---

## Dependencies
- *Python*: The core programming language used for implementation.
- *Streamlit*: A Python library for building interactive web applications.
- *NetworkX*: A Python library for creating, manipulating, and analyzing complex networks.


---
### Recommended Improvements

1. *Advanced Filtering Options:* Enhance the filtering mechanism to support multi-criteria and conditional filters, such as filtering parts by subtype, cost range, or location simultaneously.

2. *Integration of Predictive Analytics:* Incorporate predictive analytics to forecast inventory levels, bottlenecks, or transport costs based on historical trends and machine learning models.