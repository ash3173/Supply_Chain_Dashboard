# Business Group Dashboard

## Overview
The Business Group page of the Dashboard is a Streamlit-based application designed to provide comprehensive insights into business group performance, relationships, and revenue metrics over time.This tool provides insights into revenue trends, detailed information about graph nodes, and relationships between business entities. 

Key features include dynamic visualizations, interactive queries, and graph-based analyses.

---

## Data Exploration and Visualization


### **1. Business Group Schema**
A schema visualization that illustrates the structure of business groups and product families, as well as their interconnections. 
- **Range Slider**: Users can adjust timestamp ranges for tailored revenue analyses.
- **Attributes**:
  - **Business Group**: Node type, name, description, revenue, and ID.
  - **Product Family**: Node type, name, revenue, and ID.

### **2. Revenue Data Query**
This dynamic visualization highlights revenue trends over time for selected business groups over a period of time.
- **Methodology**:
  - Iterates through the range of selected timestamps.
  - Collects revenue data for each business group.
  - Stores results in a dictionary indexed by business group ID.
- **Features**:
  - Each panel corresponds to a business group.
  - X-axis: Time | Y-axis: Revenue.
  - Shaded regions emphasize performance fluctuations.

### **3. Top Business Groups Query**
Visualizes the top three business groups based on revenue performance in the selected range.
- Circular markers display revenue values and identifiers.
- Annotations highlight the time periods.
- **Methodology**:
  - Utilizes Python’s `heapq` to maintain a sorted list of top business groups.
  - Ensures only the top three entries are kept for visualization.


### **4. Node Details Query**
- **Purpose**: Fetches and displays detailed information about selected nodes.
- **Business Group Selector**: Enables exploration of specific business group data through drop-down menus.
- **Methodology**:
  - Retrieves node attributes from the session state and timestamped graph data.
  - Displays attributes in a styled table format for easy interpretation.

### **5. Neighbouring nodes visualization Graph Query**
- **Purpose**: Graph-based visualizations reveal relationships between entities, focusing on neighborhoods of selected nodes.
- **Methodology**:
  - Uses NetworkX’s `ego_graph` function to extract nodes within a defined radius.
  - Visualizes the graph with Plotly, making attributes accessible through hover effects.

---

## Code Structure

### **1. Utility Functions**
- **`time_and_memory_streamlit`**: Tracks function runtime and memory usage.
- **`create_graph`**: Generates the static schema visualization.
- **`plot_revenue`**: Creates multi-panel revenue trend plots.
- **`plot_higest_revenue`**: Visualizes the top three business groups’ revenues.
- **`plotly_ego_graph`**: Plots ego graphs using Plotly.
- **`ego_graph_query`**: Executes ego graph queries.

### **2. Streamlit Fragments**
- **`static_part`**: Manages timestamp range selection and visualizes revenue and top business groups.
- **`node_details_input`**: Facilitates user input for node-specific queries.
- **`node_details`**: Displays detailed node attributes and their ego graphs.

### **3. Main Function**
- Sets up the Streamlit interface.
- Divides the dashboard into two primary sections:
  - **Static Visualizations**: Time-series trends and schema overviews.
  - **Interactive Node Details**: Detailed exploration of individual business groups.

---

## Usage Instructions
1. Select a time range using the timestamp slider
2. Explore the business group schema
3. View revenue trends across business units
4. Select a specific business group to view its profile and a visual representation of its network.


## Performance Considerations
- Memory and time usage are tracked for key functions
- Supports large temporal graph datasets
- Responsive design with wide layout


## Dependencies

- **Streamlit**: The backbone for creating the interactive dashboard.
- **Matplotlib** and **Plotly**: Used for various dynamic visualizations.
- **NetworkX**: Provides tools for graph operations like ego graphs.
- **Heapq**: Enables efficient maintenance of the top three business groups.
- **Tracemalloc**: Monitors memory usage to optimize performance.

---


## Recommended Improvements
- Add export functionality for reports
- Implement more advanced filtering
- Add predictive analytics components



