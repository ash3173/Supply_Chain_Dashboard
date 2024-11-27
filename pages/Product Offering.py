import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

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

    profitable_products = []
    G = temporal_graph.load_graph_at_timestamp(timestamp)
    for node, attrs in G.nodes(data=True):
        if attrs.get("node_type") == "PRODUCT_OFFERING":
            making_cost = attrs.get("cost", float("inf"))
            demand = attrs.get("demand", 0)

            if making_cost <= cost_threshold and demand >= demand_threshold:
                profitable_products.append((node, making_cost, demand))
    return profitable_products

def get_top_demand_products(temporal_graph, num_timestamps, top_n=3):
    """
    Find the top N product offerings with the highest demand across timestamps.
    """
    
    demand_records = []

    for timestamp in range(num_timestamps):
        url_data = requests.get(temporal_graph.files[timestamp])
        if url_data.status_code != 200:
            continue

        data = url_data.json()
        product_offerings = get_product_offerings(data)

        for offering in product_offerings:
            product_name = offering.get("name", "Unknown Product")
            demand = offering.get("demand", 0)
            demand_records.append((timestamp, product_name, demand))

    # Sort by demand in descending order and take the top N
    sorted_records = sorted(demand_records, key=lambda x: x[2], reverse=True)
    return sorted_records[:top_n]


def main():
    st.title("Product Offerings Dashboard")

    if "temporal_graph" not in st.session_state:
        st.error("No Temporal Graph found in the session state. Please run the main script first.")
        return
    temporal_graph = st.session_state.temporal_graph
    num_timestamps = len(temporal_graph.files)


    top_products = get_top_demand_products(temporal_graph, num_timestamps)
    # Display top products in individual boxes
    st.subheader("Top Product Offerings by Demand")
    df_top = pd.DataFrame(top_products, columns=["Timestamp", "Product Name", "Demand"])

    fig_pie = px.pie(df_top, 
                 values="Demand", 
                 names="Product Name", 
                 title="Demand Share of Top Products", 
                 hover_data=["Timestamp"])
    fig_pie.update_traces(textinfo="label+percent", hoverinfo="label+value")
    st.plotly_chart(fig_pie)






        
    all_avg_costs = {}
    all_avg_demands = {}

    # Iterate through all timestamps
    for timestamp in range(len(temporal_graph.files)):
        url_data = requests.get(temporal_graph.files[timestamp])
        if url_data.status_code != 200:
            st.error(f"Failed to load data for timestamp {timestamp}. Skipping...")
            continue

        # Parse data
        data = url_data.json()

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

    # Plotting
    st.subheader("Average Cost Across Timestamps")
    fig_cost = go.Figure()
    for family_id in time_series_cost.columns:
        fig_cost.add_trace(go.Scatter(
            x=time_series_cost.index,
            y=time_series_cost[family_id],
            mode='lines+markers',
            name=f"Family {family_id}"
        ))
    fig_cost.update_layout(title="Average Cost by Product Family Across Timestamps",
                           xaxis_title="Timestamp",
                           yaxis_title="Average Cost")
    st.plotly_chart(fig_cost)

    st.subheader("Average Demand Across Timestamps")
    fig_demand = go.Figure()
    for family_id in time_series_demand.columns:
        fig_demand.add_trace(go.Scatter(
            x=time_series_demand.index,
            y=time_series_demand[family_id],
            mode='lines+markers',
            name=f"Family {family_id}"
        ))
    fig_demand.update_layout(title="Average Demand by Product Family Across Timestamps",
                             xaxis_title="Timestamp",
                             yaxis_title="Average Demand")
    st.plotly_chart(fig_demand)
    # num_timestamps = len(temporal_graph.files)

    st.divider()
    st.title("Queries")
    # Slider for timestamp selection
    timestamp = st.slider("Select Timestamp", 0, num_timestamps - 1, 0)

    # Input fields for thresholds
    demand_threshold = st.text_input("Enter Demand Threshold", "1000")
    cost_threshold = st.text_input("Enter Cost Threshold", "100")

    # Convert inputs to numerical values
    try:
        demand_threshold = int(demand_threshold)
        cost_threshold = int(cost_threshold)
    except ValueError:
        st.error("Please enter valid numerical values for thresholds.")
        return

    # Query profitable products
    if st.button("Query Profitable Products"):
        profitable_products = query_profitable_products(
            temporal_graph,
            timestamp,
            cost_threshold,
            demand_threshold
        )

        if profitable_products:
            st.subheader(f"Profitable Products at Timestamp {timestamp}")
            df = pd.DataFrame(profitable_products, columns=["Product ID", "Cost", "Demand"])
            st.dataframe(df)
        else:
            st.warning(f"No profitable products found for the given thresholds at Timestamp {timestamp}.")




if __name__ == "__main__":
    main()