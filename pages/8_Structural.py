import networkx as nx
import plotly.graph_objects as go
import streamlit as st
import numpy as np
import pandas as pd
from utils import time_and_memory_streamlit

# final function to visualize the graph
def plotly_ego_graph(G):
    show_edges = True
    EDGE_COLOR = "#B0B0B0"  # Light gray for edges
    NODE_CONFIG = {
        "BUSINESS_GROUP": {
            "color": "#E63946",  # Soft red
            "display_name": "Business Group",
            "size_multiplier": 2.0,
        },
        "PRODUCT_FAMILY": {
            "color": "#457B9D",  # Medium blue
            "display_name": "Product Family",
            "size_multiplier": 1.8,
        },
        "PRODUCT_OFFERING": {
            "color": "#1D3557",  # Deep navy
            "display_name": "Product Offering",
            "size_multiplier": 1.5,
        },
        "SUPPLIERS": {
            "color": "#2A9D8F",  # Teal
            "display_name": "Supplier",
            "size_multiplier": 1.6,
        },
        "WAREHOUSE": {
            "color": "#E9C46A",  # Golden yellow
            "display_name": "Warehouse",
            "size_multiplier": 1.7,
        },
        "FACILITY": {
            "color": "#F4A261",  # Soft orange
            "display_name": "Facility",
            "size_multiplier": 1.7,
        },
        "PARTS": {
            "color": "#264653",  # Dark teal
            "display_name": "Part",
            "size_multiplier": 1.3,
        },
    }


    # for selecting all the possible nodes for the vis.
    selected_node_types = {}
    for node_type, config in NODE_CONFIG.items():
        selected_node_types[node_type] = True

    pos = nx.kamada_kawai_layout(G)

    # Create edge trace if edges are enabled
    traces = []
    if show_edges:
        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        edge_trace = go.Scatter(
            x=edge_x,
            y=edge_y,
            line=dict(width=0.5, color=EDGE_COLOR),
            hoverinfo="none",
            mode="lines",
            name="Connections",
            opacity=0.7,  # Increased opacity for better visibility
        )
        traces.append(edge_trace)

    # print(G.nodes(data=True))

    # Create node traces with improved hover information
    for node_type, config in NODE_CONFIG.items():
        if selected_node_types[node_type]:
            node_x = []
            node_y = []
            node_text = []
            node_size = []

            for node in G.nodes():
                if G.nodes[node]["node_type"] == node_type:
                    x, y = pos[node]
                    node_x.append(x)
                    node_y.append(y)

                    # Enhanced hover information
                    degree = G.degree(node)
                    in_degree = G.in_degree(node)
                    out_degree = G.out_degree(node)

                    # Initialize hover text
                    hover_text = f"<b>{config['display_name']}</b><br>"
                    hover_text += f"ID: {node}<br>"
                    hover_text += f"Connections: {degree}<br>"
                    hover_text += f"Incoming: {in_degree}<br>"
                    hover_text += f"Outgoing: {out_degree}"

                    # Add additional node attributes if they exist
                    # node_data = G.nodes[node]
                    # st.write(G.nodes[node])
                    for key, value in G.nodes[node].items():
                        if (
                            key != "node_type"
                        ):  # Skip node_type as it's already shown
                            hover_text += f"<br>{key}: {value}"

                    node_text.append(hover_text)

                    # Calculate node size based on degree and configuration
                    base_size = np.sqrt(degree + 1) * config["size_multiplier"]
                    # scaled_size = base_size * size_scale
                    # node_size.append(
                    #     np.clip(scaled_size, MIN_NODE_SIZE, MAX_NODE_SIZE)
                    # )

            if node_x:  # Only create trace if nodes exist for this type
                node_trace = go.Scatter(
                    x=node_x,
                    y=node_y,
                    mode="markers",
                    name=f"<b>{config['display_name']}</b>",  # Bold text in legend
                    marker=dict(
                        size=40,
                        color=config["color"],
                        line=dict(width=1, color="white"),
                        opacity=0.9,  # Increased opacity
                    ),
                    text=node_text,
                    hoverinfo="text",
                    legendgroup=node_type,
                    showlegend=True,
                )
                traces.append(node_trace)

    # Create figure with improved layout and darker legend
    fig = go.Figure(
        data=traces,
        layout=go.Layout(
            title=dict(
                text="",
                x=0.5,
                y=0.95,
                font=dict(size=20, color="black"),
            ),
            showlegend=True,
            hovermode="closest",
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor="rgba(14,17,23,255)",
            paper_bgcolor="rgba(14,17,23,255)",
            # height=500,
            hoverlabel=dict(
                bgcolor="white",
                font=dict(size=12, color="black"),
                bordercolor="black",
            ),
        ),
    )

    return fig

# def plotly_ego_graph(ego_graph):
#     """
#     Visualizes the ego graph using Plotly.
#     """
#     pos = nx.spring_layout(ego_graph)
#     edge_x = []ee
#     for edge in ego_graph.edges():
#         x0, y0 = pos[edge[0]]
#         x1, y1 = pos[edge[1]]
#         edge_x.append(x0)
#         edge_y.append(y0)
#         edge_x.append(x1)
#         edge_y.append(y1)

#     edge_trace = go.Scatter(
#         x=edge_x, y=edge_y,
#         line=dict(width=0.5, color='gray'),
#         hoverinfo='none',
#         mode='lines'
#     )

#     node_x = []
#     node_y = []
#     hover_text = []
#     for node in ego_graph.nodes():
#         x, y = pos[node]
#         node_x.append(x)
#         node_y.append(y)
#         hover_text.append(f"Node {node}")

#     node_trace = go.Scatter(
#         x=node_x, y=node_y,
#         mode='markers+text',
#         hoverinfo='text',
#         marker=dict(
#             showscale=True,
#             colorscale='YlGnBu',
#             size=20,
#             colorbar=dict(thickness=15, title="Node Connections", xanchor="left", titleside="right")
#         ),
#         text=hover_text,
#         textposition="top center"
#     )

#     layout = go.Layout(
#         title="Ego Graph Visualization",
#         titlefont_size=16,
#         showlegend=False,
#         hovermode='closest',
#         xaxis=dict(showgrid=False, zeroline=False),
#         yaxis=dict(showgrid=False, zeroline=False),
#         height=600,
#         width=800
#     )

#     fig = go.Figure(data=[edge_trace, node_trace], layout=layout)
#     return fig


@time_and_memory_streamlit
def ego_graph_query(graph, node_id, radius):
    """
    Returns the ego graph for a specific node within a given radius.
    """
    ego_graph = nx.ego_graph(graph, node_id, radius=radius,undirected=True)
    return ego_graph

@time_and_memory_streamlit
def node_details_query(graph, node_id):
    """
    Returns the details of a specific node in the graph.
    """
    node_data = graph.nodes[node_id]
    # Create a DataFrame without an index
    df = pd.DataFrame({"Attribute": node_data.keys(), "Value": node_data.values()})
    return df


@time_and_memory_streamlit
def retrieve_edge_attributes(graph, node_id):
    """
    Returns a DataFrame of all edges connected to the given node along with their attributes.
    """
    edges = []
    for neighbor in graph.neighbors(node_id):
        if graph.has_edge(node_id, neighbor):
            edge_attributes = graph.get_edge_data(node_id, neighbor)
            # Flattening the attributes for better readability in the DataFrame
            edges.append({
                "From": node_id,
                "To": neighbor,
                **edge_attributes  # Add individual attribute keys as columns
            })
    # Convert to DataFrame
    return pd.DataFrame(edges)

@time_and_memory_streamlit
def find_shortest_path(directed_graph, source, destination):
    """
    Finds the shortest path between source and destination nodes and visualizes the path.

    Parameters:
        graph (nx.Graph): The graph object.
        source (str/int): Source node ID.
        destination (str/int): Destination node ID.

    Returns:
        tuple: Shortest path, length, and Plotly figure.
    """
    graph = directed_graph.to_undirected()
    try:
        # Find the shortest path and its length
        path = nx.shortest_path(graph, source=source, target=destination)
        
        length = nx.shortest_path_length(graph, source=source, target=destination)

        # Create a subgraph containing only the shortest path
        path_edges = [(path[i], path[i + 1]) for i in range(len(path) - 1)]
        subgraph = nx.Graph()
        subgraph.add_edges_from(path_edges)

        # Use spring layout for the subgraph
        pos = nx.spring_layout(subgraph)

        # Extract edge data for visualization
        edge_x = []
        edge_y = []
        for edge in subgraph.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.append(x0)
            edge_y.append(y0)
            edge_x.append(x1)
            edge_y.append(y1)
            edge_x.append(None)  # Separate edges
            edge_y.append(None)

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=2, color='red'),
            hoverinfo='none',
            mode='lines'
        )

        # Extract node data for visualization
        node_x = []
        node_y = []
        node_color = []
        hover_text = []
        for node in subgraph.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)

            # Highlight nodes based on their role in the path
            if node == source:
                node_color.append('green')  # Source
                hover_text.append(f"Source Node: {node}")
            elif node == destination:
                node_color.append('blue')  # Destination
                hover_text.append(f"Destination Node: {node}")
            else:
                node_color.append('orange')  # Intermediate
                hover_text.append(f"Intermediate Node: {node}")

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            marker=dict(
                size=20,
                color=node_color,
                line=dict(width=2, color='black')
            ),
            text=[f"{node}" for node in subgraph.nodes()],  # Display node IDs
            textposition="top center"
        )

        # Create the figure
        fig = go.Figure(data=[edge_trace, node_trace])
        fig.update_layout(
            title="Shortest Path Visualization",
            titlefont_size=16,
            showlegend=False,
            hovermode='closest',
            xaxis=dict(showgrid=False, zeroline=False),
            yaxis=dict(showgrid=False, zeroline=False),
            height=500,
            width=900
        )

        return path, length, fig

    except nx.NetworkXNoPath:
        return None, None, None
    except nx.NodeNotFound as e:
        return str(e), None, None

@time_and_memory_streamlit
def get_ancestors_descendants(graph, node_id):
    if not isinstance(graph, nx.DiGraph):
        raise TypeError("The graph must be a directed graph (nx.DiGraph).")

    if node_id not in graph:
        raise ValueError(f"Node {node_id} is not in the graph.")

    # Get ancestors
    ancestors = list(nx.ancestors(graph, node_id))

    # Get descendants
    descendants = list(nx.descendants(graph, node_id))

    return pd.DataFrame(ancestors,columns=["Ancestors"]), pd.DataFrame(descendants,columns=["Descendants"])


def main():
    st.markdown("""
    <style>
        /* Remove blank space at top and bottom */
        .block-container {
            padding-top: 1rem; /* Add some padding to avoid cutting off the title */
            padding-bottom: 0rem;
        }

        /* Adjust canvas positioning */
        .st-emotion-cache-z5fcl4 {
            position: relative;
            top: -30px; /* Adjusted to avoid cutting the title */
        }

        /* Toolbar transparency and content accessibility */
        .st-emotion-cache-18ni7ap {
            pointer-events: none;
            background: rgba(255, 255, 255, 0%); /* Use correct rgba syntax for transparency */
        }
        .st-emotion-cache-zq5wmm {
            pointer-events: auto;
            background: rgb(255, 255, 255);
            border-radius: 5px;
        }
        
    </style>
    """, unsafe_allow_html=True)

    if "temporal_graph" not in st.session_state:
        st.error("No Temporal Graph found in the session state. Please run the main script first.")
        return
    st.title("Structure Based Queries")
    st.markdown("""
            #### Select Query to Execute :
        """)
    cols1,cols2=st.columns([2,1])
    with cols2:
        timestamp = st.select_slider("Select Timestamp", options=range(len(st.session_state.temporal_graph.files)))
    
    graph = st.session_state.temporal_graph.load_graph_at_timestamp(timestamp)
    all_nodes = list(graph.nodes)

    with cols1:
        # Dropdown to select query
        query_type = st.selectbox("Choose Query", ["Select","Ego Graph", "Node Details", "Edge Attributes","Shortest Path", "Ancestors and Descendants"])

    # Execute the chosen query
    if query_type == "Ego Graph":
        with cols1:
            node_id = st.selectbox("Select Node ID for Ego Graph", all_nodes)
        radius = st.slider("Select Radius for Ego Graph", 1, 5, 2)  # Slider for radius

        # Generate the ego graph using the selected node and radius
        ego_graph = ego_graph_query(graph, node_id, radius)
        if ego_graph:
            st.write(f"Ego Graph for Node: {node_id}")
            st.write(f"Nodes: {ego_graph.number_of_nodes()}, Edges: {ego_graph.number_of_edges()}")

            # Visualize and render the ego graph with Plotly
            fig = plotly_ego_graph(ego_graph)
            st.plotly_chart(fig)  # Display the figure in Streamlit

    elif query_type == "Node Details":
        with cols1:
            node_id = st.selectbox("Select Node ID for Node Details", all_nodes)
            node_data = node_details_query(graph, node_id)
            st.table(node_data)
    
    elif query_type == "Edge Attributes":
        with cols1:
            node_id = st.selectbox("Select Node ID to Retrieve Edge Attributes", all_nodes)
            if node_id:
                edge_attributes = retrieve_edge_attributes(graph, node_id)
                if not edge_attributes.empty:
                    st.write(f"Edges connected to Node {node_id}:")
                    st.table(edge_attributes)
                else:
                    st.warning(f"No edges found for Node {node_id}.")
    
    elif query_type == "Shortest Path":
        with cols1:
            source_node = st.selectbox("Enter Source Node ID", all_nodes)
            destination_node = st.selectbox("Enter Destination Node ID", all_nodes)


        if st.button("Find Shortest Path"):
            # source_node = st.selectbox("Select Node ID to Retrieve Edge Attributes", all_nodes)
            # destination_node = st.selectbox("Select Node ID to Retrieve Edge Attributes", all_nodes)
            if source_node and destination_node:
                path, length, fig = find_shortest_path(graph, source_node, destination_node)
                if path and length:
                    st.write(f"Shortest Path from {source_node} to {destination_node}: {path}")
                    st.write(f"Path Length: {length}")

            # Display the visualization
                    st.plotly_chart(fig)
                elif path is None:
                    st.warning(f"No path exists between {source_node} and {destination_node}.")
                else:
                    st.error(f"Error: {path}")
            else:
                st.error("Please enter valid source and destination nodes.")
    
    elif query_type == "Ancestors and Descendants":
        with cols1:

            node_id = st.selectbox("Enter Node ID to Retrieve Ancestors and Descendants", all_nodes)
            if node_id:
                try:
                    if node_id not in graph.nodes:
                        raise ValueError(f"Node '{node_id}' does not exist in the graph.")
                    ancestors, descendants = get_ancestors_descendants(graph, node_id)

                    st.subheader(f"Results for Node: {node_id}")
                    st.write(f"**Ancestors ({len(ancestors)}):**")
                    if not ancestors.empty:
                        st.dataframe(ancestors)
                    else:
                        st.info("No ancestors were found.")
                    if not descendants.empty:
                        st.dataframe(descendants)
                    else:
                        st.info("No descendants were found.")
                    

                except ValueError as e:
                    st.error(str(e))
                except Exception as e:
                    st.error(f"An unexpected error occurred: {str(e)}")

    st.text(" ")  # Adds one blank line
    st.text(" ")  # Adds another blank line

    st.divider()  # Adds a horizontal divider (thin line), visually separating sections

if __name__ == "__main__":
    main()