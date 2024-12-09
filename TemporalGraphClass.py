import json
from functools import lru_cache
import networkx as nx
import requests
import streamlit as st


class TemporalGraphClass:
    def __init__(self, files):
        self.files = files  # List of JSON file paths

    # @lru_cache(maxsize=10)
    @st.cache_data
    def load_graph_at_timestamp(_self, timestamp):
        data = requests.get(_self.files[timestamp]).json()
        return _self._json_to_graph(data)

    def _json_to_graph(self, data):
        graph = nx.DiGraph() if data["directed"] else nx.Graph()
        for node_type, nodes in data["node_values"].items():
            for node in nodes:
                node_id = node[-1]
                node_attributes = dict(zip(data["node_types"][node_type], node))
                graph.add_node(node_id, **node_attributes)

        all_edge_types = data["relationship_types"]
        for link_type,link_values in data["link_values"].items():
            for edge_data in link_values :
                attributes = {}
                for j in range(len(edge_data) - 2):
                    key = all_edge_types[link_type][j]
                    attributes[key] = edge_data[j]
                graph.add_edge(edge_data[-2], edge_data[-1], **attributes)

        return graph

    @st.cache_data
    def create_node_type_index(_self, timestamp):
        """Create and cache an index for all node types."""
        data = requests.get(_self.files[timestamp]).json()  # Access _self instead of self
        node_values = data["node_values"]

        # Create an index for each node type
        node_type_index = {}
        for node_type, nodes in node_values.items():
            node_type_index[node_type] = {}
            for node in nodes:
                node_id = node[-1]  # Assuming the last element is the node ID
                node_type_index[node_type][node_id] = node

        return node_type_index