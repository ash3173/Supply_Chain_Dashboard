# TemporalGraphClass Documentation

## Overview
The **TemporalGraphClass** is a Python class designed to handle temporal graph data. It facilitates loading and managing graph states at different timestamps, allowing for efficient querying and analysis of dynamic network structures.

This class supports:
- Efficient loading of graph data from JSON files.
- Conversion of JSON data into NetworkX graph objects.
- Caching of graph states for improved performance.

---

## Imports

- **`json`**: For parsing JSON files.
- **`functools.lru_cache`**: To cache results of the `load_graph_at_timestamp` method for efficiency.
- **`networkx`**: A library for creating and manipulating complex networks and graphs.

---

## Class Definition

### **`TemporalGraphClass`**

#### **Initialization**
The class is initialized with a list of JSON file paths, each representing a different state of the temporal graph at a specific timestamp.

#### **Attributes**
- **`files`**: A list of file paths pointing to JSON data files.

#### **Methods**

### 1. **`__init__(self, files)`**
- **Parameters**:
  - `files`: A list of JSON file paths.
- **Description**:
  Initializes the class with the provided list of file paths.

---

### 2. **`load_graph_at_timestamp(self, timestamp)`**
- **Parameters**:
  - `timestamp`: An integer representing the index of the file to load.
- **Returns**:
  A NetworkX graph object constructed from the JSON data at the specified timestamp.
- **Description**:
  - Reads the graph data from the JSON file corresponding to the given timestamp.
  - Converts the data into a NetworkX graph using the `_json_to_graph` method.
  - Uses `functools.lru_cache` to cache the results for improved performance.

---

### 3. **`_json_to_graph(self, data)`**
- **Parameters**:
  - `data`: A dictionary containing graph data parsed from a JSON file.
- **Returns**:
  A NetworkX graph object.
- **Description**:
  - Constructs a directed or undirected graph based on the `"directed"` key in the JSON data.
  - Adds nodes with attributes using the `node_values` key from the JSON.
  - Creates edges based on `relationship_values`, supporting both simple and attribute-rich edges.

---

### 4. **`load_json_at_timestamp(self, timestamp)`**
- **Parameters**:
  - `timestamp`: An integer representing the index of the file to load.
- **Returns**:
  A dictionary containing graph data parsed from the JSON file.
- **Description**:
  - Loads the JSON file corresponding to the given timestamp.
  - Validates file existence and parses its contents.
  - Caches results for efficiency.

---

### 5. **`create_node_type_index(self, timestamp)`**
- **Parameters**:
  - `timestamp`: An integer representing the index of the file to load.
- **Returns**:
  A dictionary indexing nodes by type and ID.
- **Description**:
  - Loads the graph data for the given timestamp using `load_json_at_timestamp`.
  - Creates an index mapping node types to their attributes and IDs.
  - Facilitates efficient querying of node attributes.

---

## Graph Construction Logic

### Nodes:
- Extracted from the `node_values` key in the JSON.
- Each node is defined by an ID and attributes derived from its type.

### Edges:
- Extracted from the `relationship_values` key in the JSON.
- Directed or undirected edges are created based on the `"directed"` key.
- Edges can include additional attributes like weights or relationships.

---

## Caching Mechanisms

### 1. **`Caching`**
- Used in the `load_json_at_timestamp` method to cache loaded JSON data.
- Ensures that frequently accessed graph states are not repeatedly read from disk, improving performance.

### 2. **`functools.lru_cache`**
- Applied to the `load_graph_at_timestamp` method to cache converted NetworkX graphs.
- Reduces computational overhead when accessing previously loaded graph states.

---

## Example Usage

To instantiate and use the `TemporalGraphClass`:

```python
files = ['path/to/json1.json', 'path/to/json2.json']
temporal_graph = TemporalGraphClass(files)

# Load graph at timestamp 0
graph_at_time_0 = temporal_graph.load_graph_at_timestamp(0)

# Perform operations on the graph
nodes = graph_at_time_0.nodes()
edges = graph_at_time_0.edges()

# Create a node type index
node_index = temporal_graph.create_node_type_index(0)
```

---

## Performance Considerations

- **Caching**: The combination of `@st.cache_data` and `lru_cache` ensures that both raw JSON data and processed graph objects are efficiently reused.
- **Flexibility**: Supports both directed and undirected graphs.
- **Scalability**: Handles large JSON datasets with complex node and edge relationships.

---

## Recommended Improvements
1. Add validation for JSON schema to ensure compatibility with the class.
2. Implement logging for debugging and monitoring graph loading operations.
3. Extend support for additional graph formats (e.g., CSV, XML).
4. Provide utility methods for common graph operations (e.g., subgraph extraction, pathfinding).

