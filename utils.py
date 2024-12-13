import plotly.graph_objects as go
import networkx as nx
import time
import tracemalloc
import functools
import streamlit as st
from pyvis.network import Network
import os

def time_and_memory_streamlit(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Start tracking memory and time
        tracemalloc.start()
        start_time = time.time()

        try:
            result = func(*args, **kwargs)
        finally:
            # Calculate memory and time usage
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            end_time = time.time()
            elapsed_time = end_time - start_time

            # Display results in Streamlit
            st.write(f"**Function Name:** `{func.__name__}`")
            st.write(f"**Time Taken:** `{elapsed_time:.2f} seconds`")
            st.write(f"**Memory Usage:** `{current / 1024:.2f} KiB` (Current), `{peak / 1024:.2f} KiB` (Peak)")

        return result
    return wrapper


def plotly_ego_graph(ego_graph):
    """
    Visualizes the ego graph using Plotly, displaying node IDs as labels and attributes on hover.
    """
    pos = nx.spring_layout(ego_graph)
    
    # Edges
    edge_x = []
    edge_y = []
    edge_hover_text = []

    for edge in ego_graph.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.append(x0)
        edge_y.append(y0)
        edge_x.append(x1)
        edge_y.append(y1)
        edge_x.append(None)  # To separate edges visually
        edge_y.append(None)

        # Format hover text for edges
        attributes = edge[2]
        hover_details = [f"{key}: {value}" for key, value in attributes.items()]
        edge_hover_text.append("<br>".join(hover_details))

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=0.5, color="gray"),
        hoverinfo="text",
        hovertext=edge_hover_text,  # Show edge attributes on hover
        mode="lines"
    )

    # Nodes
    node_x = []
    node_y = []
    node_ids = []
    node_hover_text = []

    for node in ego_graph.nodes(data=True):
        x, y = pos[node[0]]
        node_x.append(x)
        node_y.append(y)
        node_ids.append(str(node[0]))  # Use node ID as label

        # Format hover text for nodes
        attributes = node[1]
        hover_details = [f"{key}: {value}" for key, value in attributes.items()]
        node_hover_text.append("<br>".join(hover_details))

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",  # Display labels with text
        text=node_ids,  # Node IDs as labels
        textposition="top center",
        hoverinfo="text",
        hovertext=node_hover_text,  # Show attributes on hover
        marker=dict(
            showscale=False,
            colorscale="YlGnBu",
            size=20,
            color=[1] * len(node_x),
        ),
    )

    layout = go.Layout(
        title=dict(
            text="Ego Graph Visualization",
            x=0.0,
            font=dict(size=18)
        ),
        showlegend=False,
        hovermode="closest",
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False),
        height=400,
        margin=dict(l=80, r=40, t=80, b=50),  # Adjust margins
    )

    fig = go.Figure(data=[edge_trace, node_trace], layout=layout)
    return fig


def ego_graph_query(graph, node_id, radius):
    """
    Returns the ego graph for a specific node within a given radius.
    """
    ego_graph = nx.ego_graph(graph, node_id, radius=radius,undirected=True)
    return ego_graph


def visualize_graph():
    # Initialize PyVis Network with a background color
    net = Network(height='400px', width='100%', directed=True, notebook=False, bgcolor='white', font_color='black')

    # Define node types with attributes
    node_types = {
        "BUSINESS_GROUP": {"color": "#E63946", "size": 20, "properties": "node_type, name, description, revenue, id"},
        "PRODUCT_FAMILY": {"color": "#457B9D", "size": 18, "properties": "node_type, name, revenue, id"},
        "PRODUCT_OFFERING": {"color": "#1D3557", "size": 15, "properties": "node_type, name, cost, demand, id"},
        "SUPPLIERS": {"color": "#2A9D8F", "size": 16, "properties": "node_type, name, location, reliability, size, size_category, supplied_part_types, id"},
        "WAREHOUSE": {"color": "#E9C46A", "size": 17, "properties": "node_type, name, type, location, size_category, max_capacity, current_capacity, safety_stock, max_parts, capacity, id"},
        "FACILITY": {"color": "#F4A261", "size": 17, "properties": "node_type, name, type, location, max_capacity, operating_cost, id"},
        "PARTS": {"color": "#264653", "size": 13, "properties": "node_type, name, type, subtype, cost, importance_factor, valid_from, valid_till, id"},
    }

    # Define relationships
    relationship_types = {
        "BUSINESS_GROUPToPRODUCT_FAMILY": {"color": "#A8DADC", "properties": "relationship_type, source, target"},
        "PRODUCT_FAMILYToPRODUCT_OFFERING": {"color": "#457B9D", "properties": "relationship_type, source, target"},
        "SUPPLIERSToWAREHOUSE": {"color": "#2A9D8F", "properties": "relationship_type, transportation_cost, lead_time, source, target"},
        "WAREHOUSEToPARTS": {"color": "#E9C46A", "properties": "relationship_type, inventory_level, storage_cost, source, target"},
        "WAREHOUSEToPRODUCT_OFFERING": {"color": "#1D3557", "properties": "relationship_type, inventory_level, storage_cost, source, target"},
        "FACILITYToPARTS": {"color": "#F4A261", "properties": "relationship_type, production_cost, lead_time, quantity, source, target"},
        "FACILITYToPRODUCT_OFFERING": {"color": "#264653", "properties": "relationship_type, product_cost, lead_time, quantity, source, target"},
        "PARTSToFACILITY": {"color": "#E63946", "properties": "relationship_type, quantity, distance, transport_cost, lead_time, source, target"},
    }

    # Add nodes
    for node_type, attributes in node_types.items():
        # Format properties for vertical display
        formatted_properties = "\n".join(attributes["properties"].split(", "))
        net.add_node(node_type, label=node_type, color=attributes["color"], size=attributes["size"], title=formatted_properties)

    # Add edges
    for rel_type, attributes in relationship_types.items():
        source, target = rel_type.split("To")
        formatted_properties = "\n".join(attributes["properties"].split(", "))
        net.add_edge(source, target, color=attributes["color"], title=formatted_properties)

    # Save the graph to an HTML file
    net.save_graph("graph_schema.html")
