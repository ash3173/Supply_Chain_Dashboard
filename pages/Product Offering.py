import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
# from plotly import graph_objects as go
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import networkx as nx
import time
import tracemalloc
import functools

def time_and_memory_streamlit(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Start tracking memory and time
        tracemalloc.start()
        start_time = time.time()

        try:
            # Call the actual function
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

st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
    )

@time_and_memory_streamlit
def node_details(product_data, product_id):
    col1, col2 = st.columns(2)

    with col1:
        st.write("### Product Offering Info")

        # Define the attributes of the product offering
        attributes = [
            ("Node Type", "🔗"),
            ("Name", "📛"),
            ("Cost", "💰"),
            ("Demand", "📈"),
            ("ID", "🆔")
        ]

        # Style for the no-border table
        st.markdown("""
            <style>
                .product-table {
                    width: 100%;
                    margin-top: 20px;
                    border-collapse: collapse;
                    font-size: 16px;
                    font-family: Arial, sans-serif;
                }
                .product-table td {
                    padding: 8px 12px;
                }
                .product-table td:first-child {
                    font-weight: bold;
                    color: #0d47a1; /* Blue color for attribute labels */
                    width: 40%;
                    text-align: left;
                }
                .product-table td:last-child {
                    color: #2596be; /* Gray color for attribute values */
                    width: 60%;
                    text-align: left;
                }
            </style>
        """, unsafe_allow_html=True)

        found = False

        # Loop through product data to find matching Product ID and display details
        for val in product_data:
            if product_id and product_id in val:
                found = True

                # Create a no-border table for displaying attributes and values
                table_rows = ""
                for attr, icon in attributes:
                    table_rows += f"<tr><td>{icon} {attr}:</td><td>{val[attributes.index((attr, icon))]}</td></tr>"

                # Display the table
                st.markdown(
                    f"""
                    <table class="product-table">
                        {table_rows}
                    </table>
                    """,
                    unsafe_allow_html=True
                )

        if not found:
            st.warning('Enter a valid product ID')
    with col2:
        if found:
            graph=st.session_state.temporal_graph.load_graph_at_timestamp(2)
            ego_graph = ego_graph_query(graph, product_id, 2)
            if ego_graph:
                st.write(f"### Neighbors for {product_id}")
                # st.write(f"Ego Graph for Node: {supplier_id}")
                # st.write(f"Nodes: {ego_graph.number_of_nodes()}, Edges: {ego_graph.number_of_edges()}")

                # Visualize and render the ego graph with Plotly
                fig = plotly_ego_graph(ego_graph)
                st.plotly_chart(fig)  # Display the figure in Streamlit
@st.fragment
def pre_detail(po_data):
    
    col1,col2=st.columns([2,1])
    with col1:
        st.write("### Product Offering Details Viewer")
        all_po = ["Select Product Offering"]
        for po in po_data:
            all_po.append(po[-1])
        po_id_input = st.selectbox("Choose Product Offering Id",all_po)
    
    if po_id_input!="Select Product Offering":
        node_details(po_data, po_id_input)


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
    ego_graph = nx.ego_graph(graph, node_id, radius=radius)
    return ego_graph



def get_product_offering_ids(temporal_graph, timestamp):
    """
    Retrieve all available PRODUCT_OFFERING IDs at the given timestamp.
    """
    G = temporal_graph.load_graph_at_timestamp(timestamp)
    return [
        node_id
        for node_id, data in G.nodes(data=True)
        if data.get("node_type") == "PRODUCT_OFFERING"
    ]


def create_graph():
    # Define node attributes
    nodes = {
        "PRODUCT_OFFERING": ["node_type", "name", "cost", "demand", "id"],
        "PRODUCT_FAMILY": ["node_type", "name", "revenue", "id"],
        "WAREHOUSE": ["node_type", "name", "type", "location", "size_category", "max_capacity", "current_capacity", "safety_stock", "max_parts", "capacity", "id"],
        "FACILITY": ["node_type", "name", "type", "location", "max_capacity", "operating_cost", "id"]
    }

    # Define edge attributes
    edges = {
        "PRODUCT_FAMILYToPRODUCT_OFFERING": ["relationship_type", "source", "target"],
        "WAREHOUSEToPRODUCT_OFFERING": ["relationship_type", "inventory_level", "storage_cost", "source", "target"],
        "FACILITYToPRODUCT_OFFERING": ["relationship_type", "product_cost", "lead_time", "quantity", "source", "target"]
    }

    # Create a new figure
    fig = go.Figure()

    # Add edge: PRODUCT_FAMILY to PRODUCT_OFFERING
    fig.add_trace(go.Scatter(
        x=[0, 0.5], y=[0, -0.3], mode='lines', line=dict(width=2, color='white'),
        hoverinfo='text',
        text=['<b>PRODUCT_FAMILYToPRODUCT_OFFERING</b><br>' + '<br>'.join(edges["PRODUCT_FAMILYToPRODUCT_OFFERING"])]
    ))

    # Add edge: WAREHOUSE to PRODUCT_OFFERING
    fig.add_trace(go.Scatter(
        x=[0.5, 1], y=[-0.3, -0.6], mode='lines', line=dict(width=2, color='white'),
        hoverinfo='text',
        text=['<b>WAREHOUSEToPRODUCT_OFFERING</b><br>' + '<br>'.join(edges["WAREHOUSEToPRODUCT_OFFERING"])]
    ))

    # Add edge: FACILITY to PRODUCT_OFFERING
    fig.add_trace(go.Scatter(
        x=[1, 1.5], y=[-0.6, -0.9], mode='lines', line=dict(width=2, color='white'),
        hoverinfo='text',
        text=['<b>FACILITYToPRODUCT_OFFERING</b><br>' + '<br>'.join(edges["FACILITYToPRODUCT_OFFERING"])]
    ))

    # Add PRODUCT_FAMILY node
    fig.add_trace(go.Scatter(
        x=[0], y=[0], mode='markers+text', marker=dict(size=15, color='cyan'),
        text=['PRODUCT_FAMILY'], textposition='top center', hoverinfo='text',
        hovertext='<b>PRODUCT_FAMILY</b><br>' + '<br>'.join(nodes["PRODUCT_FAMILY"])
    ))

    # Add PRODUCT_OFFERING node
    fig.add_trace(go.Scatter(
        x=[0.5], y=[-0.3], mode='markers+text', marker=dict(size=15, color='orange'),
        text=['PRODUCT_OFFERING'], textposition='top center', hoverinfo='text',
        hovertext='<b>PRODUCT_OFFERING</b><br>' + '<br>'.join(nodes["PRODUCT_OFFERING"])
    ))

    # Add WAREHOUSE node
    fig.add_trace(go.Scatter(
        x=[1], y=[-0.6], mode='markers+text', marker=dict(size=15, color='green'),
        text=['WAREHOUSE'], textposition='top center', hoverinfo='text',
        hovertext='<b>WAREHOUSE</b><br>' + '<br>'.join(nodes["WAREHOUSE"])
    ))

    # Add FACILITY node
    fig.add_trace(go.Scatter(
        x=[1.5], y=[-0.9], mode='markers+text', marker=dict(size=15, color='red'),
        text=['FACILITY'], textposition='top center', hoverinfo='text',
        hovertext='<b>FACILITY</b><br>' + '<br>'.join(nodes["FACILITY"])
    ))

    # Update layout for visibility
    fig.update_layout(
        title=dict(
            text="Product Offering Schema",
            x=0, xanchor='left', yanchor='top'
        ),
        height=400,
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis=dict(
            showgrid=False, zeroline=False, showticklabels=False,
            range=[-0.2, 1.7]  # Adjust x-axis range for padding
        ),
        yaxis=dict(
            showgrid=False, zeroline=False, showticklabels=False,
            range=[-1.1, 0.2]  # Adjust y-axis range for padding
        ),
        showlegend=False,
        font=dict(color="white", size=10),
        hoverlabel=dict(bgcolor="black", font_color="white"),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )

    return fig


def get_product_offerings(data):
    """
    Extracts all PRODUCT_OFFERING nodes from the given data.
    """
    product_offerings = []

    # Extract node attributes for PRODUCT_OFFERING nodes
    for node_type, nodes in data.get("node_values", {}).items():
        if node_type == "PRODUCT_OFFERING":
            for node in nodes:
                node_attributes = dict(zip(data["node_types"][node_type], node))
                product_offerings.append(node_attributes)

    return product_offerings


def get_product_family_to_offering_relationships(data):
    """
    Extracts PRODUCT_FAMILYToPRODUCT_OFFERING relationships from the given data.
    """
    family_to_offering = []

    # Extract edge attributes for PRODUCT_FAMILYToPRODUCT_OFFERING relationships
    relationship_type = "PRODUCT_FAMILYToPRODUCT_OFFERING"
    if relationship_type in data.get("link_values", {}):
        for edge_data in data["link_values"][relationship_type]:
            edge_attributes = dict(zip(data["relationship_types"][relationship_type], edge_data))
            family_to_offering.append(edge_attributes)

    return family_to_offering

def query_profitable_products(temporal_graph, timestamp, cost_threshold, demand_threshold):
    """
    Query 1: Find profitable products based on cost and demand thresholds.
    """
    profitable_products = []
    G = temporal_graph.load_graph_at_timestamp(timestamp)
    for node, attrs in G.nodes(data=True):
        if attrs.get("node_type") == "PRODUCT_OFFERING":
            making_cost = attrs.get("cost", float("inf"))
            demand = attrs.get("demand", 0)

            if making_cost <= cost_threshold and demand >= demand_threshold:
                profitable_products.append((node, making_cost, demand))
    return profitable_products

def query_product_cost_demand_across_timestamps(temporal_graph, product_offering_id):
    """
    Query 2: Retrieve the cost and demand of a product offering across timestamps.
    """
    costs = []
    demands = []

    for timestamp, file_url in enumerate(temporal_graph.files):
        # url_data = requests.get(file_url)
        # if url_data.status_code != 200:
        #     continue

        # data = url_data.json()
        data = st.session_state.temporal_graph.load_json_at_timestamp(timestamp)
        product_offerings = get_product_offerings(data)
        for offering in product_offerings:
            if offering.get("id") == product_offering_id:
                costs.append((timestamp, offering.get("cost", 0)))
                demands.append((timestamp, offering.get("demand", 0)))
                break

    return costs, demands


def query_and_plot_costs_plotly(temporal_graph, product_offering_id, timestamp):
    """
    Query and visualize product costs and storage costs for a given PRODUCT_OFFERING using Plotly.
    """
    G = temporal_graph.load_graph_at_timestamp(timestamp)

    # Retrieve product cost from facilities
    facility_costs = {}
    for u, v, attrs in G.edges(data=True):
        if (
            attrs.get("relationship_type") == "FACILITYToPRODUCT_OFFERING"
            and v == product_offering_id
        ):
            facility_name = G.nodes[u].get("name", u)  # Default to ID if name not present
            product_cost = attrs.get("product_cost", 0)
            facility_costs[facility_name] = product_cost

    # Retrieve storage cost from warehouses
    warehouse_costs = {}
    for u, v, attrs in G.edges(data=True):
        if (
            attrs.get("relationship_type") == "WAREHOUSEToPRODUCT_OFFERING"
            and v == product_offering_id
        ):
            warehouse_name = G.nodes[u].get("name", u)  # Default to ID if name not present
            storage_cost = attrs.get("storage_cost", 0)
            warehouse_costs[warehouse_name] = storage_cost

    # Plot product costs per facility
    if facility_costs:
        st.subheader("Product Cost per Facility")
        facility_fig = px.bar(
            x=list(facility_costs.keys()),
            y=list(facility_costs.values()),
            labels={"x": "Facilities", "y": "Product Cost"},
            title="Product Cost per Facility",
        )
        st.plotly_chart(facility_fig)
    else:
        st.warning("No facilities found storing the given product offering.")

    # Plot storage costs per warehouse
    if warehouse_costs:
        st.subheader("Storage Cost per Warehouse")
        warehouse_fig = px.bar(
            x=list(warehouse_costs.keys()),
            y=list(warehouse_costs.values()),
            labels={"x": "Warehouses", "y": "Storage Cost"},
            title="Storage Cost per Warehouse",
        )
        st.plotly_chart(warehouse_fig)
    else:
        st.warning("No warehouses found storing the given product offering.")



def get_top_demand_products(temporal_graph, num_timestamps, top_n=3):
    """
    Find the top N product offerings with the highest demand across timestamps.
    """
    
    demand_records = []

    for timestamp in range(num_timestamps):
        # url_data = requests.get(temporal_graph.files[timestamp])
        # if url_data.status_code != 200:
        #     continue

        # data = url_data.json()
        data = st.session_state.temporal_graph.load_json_at_timestamp(timestamp)
        product_offerings = get_product_offerings(data)

        for offering in product_offerings:
            product_name = offering.get("name", "Unknown Product")
            demand = offering.get("demand", 0)
            demand_records.append((timestamp, product_name, demand))

    # Sort by demand in descending order and take the top N
    sorted_records = sorted(demand_records, key=lambda x: x[2], reverse=True)
    return sorted_records[:top_n]





def main():
    # Adjust global Streamlit styling
    st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem; /* Reduce top padding */
            padding-bottom: 0rem;
        }
        .css-1v3fvcr {
            margin-top: 0rem;
            margin-bottom: 0rem;
        }
    </style>
    """, unsafe_allow_html=True)
    st.title("Product Offerings Dashboard")

    if "temporal_graph" not in st.session_state:
        st.error("No Temporal Graph found in the session state. Please run the main script first.")
        return
    temporal_graph = st.session_state.temporal_graph
    num_timestamps = len(temporal_graph.files)


    top_products = get_top_demand_products(temporal_graph, num_timestamps)
    # Display top products in individual boxes
    st.text("Top Product Offerings by Demand")
    # Get the top products by demand
    top_products = get_top_demand_products(temporal_graph, num_timestamps)

    # st.subheader("Top Product Offerings by Demand")

    # Visualize each product using Streamlit's metric cards
    if top_products:
        cols = st.columns(len(top_products))

        for i, product in enumerate(top_products):
            timestamp, product_name, demand = product
            with cols[i]:
                # Format demand to 3 decimal places
                formatted_demand = f"{demand:.3f}"
                st.metric(label=f"Product: {product_name} (Timestamp: {timestamp})", value=f"{formatted_demand}")
    else:
        st.info("No product offerings data found.")

    # cols = st.columns(3)

    # i = 0
    # if top_products:
    #     for product in top_products:
    #         timestamp, product_name, demand = product
    #         fig = plot_highest_demand(demand, product_name, timestamp)
    #         with cols[i] :
    #             st.pyplot(fig)
    #         i += 1
    # else:
    #     st.info("No product offerings data found.")
    
    


        
    all_avg_costs = {}
    all_avg_demands = {}

    # Iterate through all timestamps
    for timestamp in range(len(temporal_graph.files)):
        data = st.session_state.temporal_graph.load_json_at_timestamp(timestamp)

        # Retrieve PRODUCT_FAMILY to PRODUCT_OFFERING relationships
        family_to_offering_relationships = get_product_family_to_offering_relationships(data)

        # Retrieve PRODUCT_OFFERING nodes
        product_offerings = get_product_offerings(data)

        # Create a lookup dictionary for PRODUCT_OFFERING nodes by ID
        offering_lookup = {po["id"]: po for po in product_offerings}

        # Calculate average cost and demand for each product family
        family_avg_cost = {}
        family_avg_demand = {}

        for relationship in family_to_offering_relationships:
            source = relationship["source"]  # PRODUCT_FAMILY ID
            target = relationship["target"]  # PRODUCT_OFFERING ID

            if target in offering_lookup:
                offering = offering_lookup[target]
                cost = offering.get("cost", 0)
                demand = offering.get("demand", 0)

                if source not in family_avg_cost:
                    family_avg_cost[source] = []
                    family_avg_demand[source] = []

                family_avg_cost[source].append(cost)
                family_avg_demand[source].append(demand)

        # Store average values for the timestamp
        all_avg_costs[timestamp] = {family: sum(costs) / len(costs) for family, costs in family_avg_cost.items()}
        all_avg_demands[timestamp] = {family: sum(demands) / len(demands) for family, demands in family_avg_demand.items()}

    # Convert data into time-series format for plotting
    time_series_cost = pd.DataFrame(all_avg_costs).T.fillna(0)
    time_series_demand = pd.DataFrame(all_avg_demands).T.fillna(0)
    st.divider()
    # Plotting
    cols0,cols1,cols2=st.columns([1,2,2])
    with cols0:
        fig = create_graph()
        st.plotly_chart(fig, use_container_width=True)
    with cols1:

        fig_cost = go.Figure()
        for family_id in time_series_cost.columns:
            fig_cost.add_trace(go.Scatter(
                x=time_series_cost.index,
                y=time_series_cost[family_id],
                mode='lines+markers',
                name=f"Family {family_id}"
            ))
        fig_cost.update_layout( title=dict(
                                text="Average Cost of Product Family Across Timestamps",
                                x=0,         # Horizontal position of the title (0 = far left, 1 = far right, 0.5 = center)
                                xanchor='left',  # Anchor the title to the center horizontally
                                y=0.964,        # Vertical position of the title (1 = top, 0 = bottom)
                                yanchor='top'   # Anchor the title to the top vertically
                            ),
                            xaxis_title="Timestamp",
                            height=400,
                            width=600,
                            yaxis_title="Average Cost")
        st.plotly_chart(fig_cost)

    with cols2:

        fig_demand = go.Figure()
        for family_id in time_series_demand.columns:
            fig_demand.add_trace(go.Scatter(
                x=time_series_demand.index,
                y=time_series_demand[family_id],
                mode='lines+markers',
                name=f"Family {family_id}"
            ))
        fig_demand.update_layout(title=dict(
                                text="Average Demand of Product Family Across Timestamps",
                                x=0,         # Horizontal position of the title (0 = far left, 1 = far right, 0.5 = center)
                                xanchor='left',  # Anchor the title to the center horizontally
                                y=0.964,        # Vertical position of the title (1 = top, 0 = bottom)
                                yanchor='top'   # Anchor the title to the top vertically
                                ),
                                height=400,
                                width=600,
                                xaxis_title="Timestamp",
                                yaxis_title="Average Demand")
        st.plotly_chart(fig_demand)
        # num_timestamps = len(temporal_graph.files)

    st.divider()
    po_data = data["node_values"]["PRODUCT_OFFERING"]
    pre_detail(po_data)
    
    st.divider()

    query_options = ["Profitable Products", "Cost and Demand Across Timestamps", "Storage Cost Analysis"]
    selected_query = st.selectbox("Select a Query", query_options)

    if selected_query == "Profitable Products":
        # Query 1
        timestamp = st.slider("Select Timestamp", 0, num_timestamps - 1, 0)
        demand_threshold = st.text_input("Enter Demand Threshold", "10")
        cost_threshold = st.text_input("Enter Cost Threshold", "100")

        try:
            demand_threshold = int(demand_threshold)
            cost_threshold = int(cost_threshold)
        except ValueError:
            st.error("Please enter valid numerical values for thresholds.")
            return

        if st.button("Query Profitable Products"):
            profitable_products = query_profitable_products(
                temporal_graph,
                timestamp,
                cost_threshold,
                demand_threshold
            )

            if profitable_products:
                st.subheader(f"Profitable Products at Timestamp {timestamp}")
                # Display as a list
                st.write("Profitable Products (ID, Cost, Demand):")
                for product in profitable_products:
                    st.write(f"- ID: {product[0]}, Cost: {product[1]}, Demand: {product[2]}")
            else:
                st.warning(f"No profitable products found for the given thresholds at Timestamp {timestamp}.")

    elif selected_query == "Cost and Demand Across Timestamps":
        st.subheader("Cost and Demand Across Timestamps")

        # Select Timestamp
        timestamp = st.slider("Select Timestamp", 0, num_timestamps - 1, 0)

        # Dynamically retrieve PRODUCT_OFFERING IDs for the selected timestamp
        product_offering_ids = get_product_offering_ids(temporal_graph, timestamp)

        if product_offering_ids:
            product_offering_id = st.selectbox(
                "Select PRODUCT_OFFERING ID",
                options=product_offering_ids,
                format_func=lambda x: f"{x}",
            )
        else:
            st.warning("No PRODUCT_OFFERING IDs available for the selected timestamp.")
            return

        if st.button("Query Cost and Demand"):
            costs, demands = query_product_cost_demand_across_timestamps(temporal_graph, product_offering_id)

            if costs and demands:
                # Plot Cost
                cost_df = pd.DataFrame(costs, columns=["Timestamp", "Cost"])
                fig_cost = px.line(cost_df, x="Timestamp", y="Cost", title="Cost Across Timestamps")
                st.plotly_chart(fig_cost)

                # Plot Demand
                demand_df = pd.DataFrame(demands, columns=["Timestamp", "Demand"])
                fig_demand = px.line(demand_df, x="Timestamp", y="Demand", title="Demand Across Timestamps")
                st.plotly_chart(fig_demand)
            else:
                st.warning(f"No data found for Product Offering ID {product_offering_id}.")


    elif selected_query == "Storage Cost Analysis":
        st.subheader("Storage Cost Analysis")

        # Select Timestamp
        timestamp = st.slider("Select Timestamp", 0, num_timestamps - 1, 0)

        # Dynamically retrieve PRODUCT_OFFERING IDs for the selected timestamp
        product_offering_ids = get_product_offering_ids(temporal_graph, timestamp)

        if product_offering_ids:
            product_offering_id = st.selectbox(
                "Select PRODUCT_OFFERING ID",
                options=product_offering_ids,
                format_func=lambda x: f"{x}",
            )
        else:
            st.warning("No PRODUCT_OFFERING IDs available for the selected timestamp.")
            return

        if st.button("Analyze Costs"):
            query_and_plot_costs_plotly(temporal_graph, product_offering_id, timestamp)
      



if __name__ == "__main__":
    main()