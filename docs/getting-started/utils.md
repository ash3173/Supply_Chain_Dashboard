



# Utility Functions Documentation

## Overview
The Supply Chain Dashboard utilizes a collection of utility functions to enhance performance, manage data, and create visualizations. These utilities are essential for the smooth operation of the dashboard and provide common functionality across different components.

## Performance Monitoring

### time_and_memory_streamlit
This is a decorator function, `time_and_memory_streamlit`, which tracks execution time and memory usage for selected functions. Results are displayed in real-time on the Streamlit interface, making performance monitoring seamless.

```python
@time_and_memory_streamlit
def your_function():
    # Function implementation
```

#### Features:
- Tracks function execution time
- Monitors memory usage
- Displays metrics in Streamlit interface
- Helps identify performance bottlenecks

## Graph Utilities

### plotly_ego_graph
Generates an interactive Plotly visualization of an ego graph.

```python
def plotly_ego_graph(graph, node_id, radius=1):
    # Creates interactive ego graph visualization
```

#### Ego Graph Visualization**
A spring-layout graph visualized with Plotly, showing the selected node’s relationships.
- **Details**:
  - Nodes and edges are positioned dynamically.
  - Interactive hover text displays node and edge attributes.
  - Highlights node connectivity for deeper insights.

#### Parameters:
- `graph`: NetworkX graph object
- `node_id`: Center node for ego graph
- `radius`: Number of hops from center node (default: 1)


## Query Functions

### ego_graph_query
Executes ego graph queries on the supply chain network.

```python
def ego_graph_query(graph, node_id, radius=1):
    # Performs ego graph query
```

#### Features:
- Configurable search radius
- Node type filtering
- Relationship type filtering
- Attribute selection

## Best Practices

### Performance Optimization
- Use appropriate caching decorators
- Monitor memory usage
- Optimize large data operations
- Implement lazy loading

### Data Management
- Validate input data
- Handle missing values
- Implement data type checking
- Use appropriate data structures

### Visualization
- Maintain consistent styling
- Implement responsive designs
- Handle large datasets efficiently
- Provide interactive features

### Error Handling
- Implement comprehensive error catching
- Provide meaningful error messages
- Log errors appropriately
- Implement recovery mechanisms


## Dependencies
- NetworkX: Graph operations
- Plotly: Interactive visualizations
- Streamlit: UI components
- Pandas: Data manipulation
- NumPy: Numerical operationss