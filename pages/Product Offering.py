import streamlit as st
import requests
import networkx as nx
import plotly.graph_objects as go

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
    )

    fig = go.Figure(data=[edge_trace, node_trace], layout=layout)

    return fig

def ego_graph_query(graph, node_id, radius):
    """
    Returns the ego graph for a specific node within a given radius.
    """
    ego_graph = nx.ego_graph(graph, node_id, radius=radius)
    return ego_graph



def main() :

    if "temporal_graph" not in st.session_state:
        st.error("No Temporal Graph found in the session state. Please run the main script first.")
        return

    timestamp = 2

    url_data = requests.get(st.session_state.temporal_graph.files[timestamp])
    if url_data.status_code != 200:
        st.error("Failed to load data from the server.")
        return
    data = url_data.json()

    # static graph by balalji

    all_product_ids = ["Select"]
    for product in data["node_values"]["PRODUCT_OFFERING"].values():
        all_product_ids.append(product[-1])

    product_id = st.selectbox("Select a product", all_product_ids)
    cols = st.columns(2)

    with cols[0]:
        # product id details 
        pass

    with cols[1]:
       if product_id != "Select":
            graph=st.session_state.temporal_graph.load_graph_at_timestamp(1)
            ego_graph = ego_graph_query(graph, product_id, 1)

            if ego_graph:
                st.write(f"### Neighbors for {product_id}")
                # st.write(f"Ego Graph for Node: {supplier_id}")
                # st.write(f"Nodes: {ego_graph.number_of_nodes()}, Edges: {ego_graph.number_of_edges()}")

                # Visualize and render the ego graph with Plotly
                fig = plotly_ego_graph(ego_graph)
                st.plotly_chart(fig)

    queries = ["Select" ,"Find the change in cost of product offering over time",
               "Find the change in demand of product offering over time",
               "Find the cost to the product offering in differnet warehouse",
               "Find the cost to produce the product in different facilities",
               "Query the products within a particular threshold of cost and demand"
    ]

    query = st.selectbox("Select a query", queries)


    
if __name__ == "__main__":
    main()