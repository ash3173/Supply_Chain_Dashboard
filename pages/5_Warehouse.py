import streamlit as st
import json
import plotly.graph_objects as go
import altair as alt
import requests
import pandas as pd
import networkx as nx
import time
import tracemalloc
import functools
st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
    )
from utils import time_and_memory_streamlit,plotly_ego_graph,ego_graph_query
def get_product_offering_ids(graph):

        return [
            node_id
            for node_id, data in graph.nodes(data=True)
            if data.get("node_type") == "PRODUCT_OFFERING"
        ]
def static_part():
    timestamp = 2
    
    # url_data = requests.get(st.session_state.temporal_graph.files[timestamp])
    # if url_data.status_code != 200:
    #     st.error("Failed to load data from the server.")
    #     return
    # data = url_data.json()
    data = st.session_state.temporal_graph.load_json_at_timestamp(timestamp)
    
    graph = st.session_state.temporal_graph.load_graph_at_timestamp(timestamp)
    
    warehouse_nodes = data["node_values"]["WAREHOUSE"]
    warehouse_data = {
        "supplier": {},
        "subassembly": {},
        "lam": {}
    }

    warehouse_size = {
        "small" : 0 ,
        "medium" : 0,
        "large" : 0
    }

    for warehouse in warehouse_nodes:
        type = warehouse[2]
        state = warehouse[3]
        size = warehouse[4]

        warehouse_size[size] += 1
        if state not in warehouse_data[type]:
            warehouse_data[type][state] = 0

        warehouse_data[type][state] += 1

    col1, col2, col3 = st.columns([1,4,1.5], gap='medium')

    with col1:
        fig = create_graph()
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = create_warehouse_map(warehouse_data)
        st.plotly_chart(fig, use_container_width=True)  # Display the figure within the column


    with col3:
        fig = donut_chart(warehouse_size)
        st.plotly_chart(fig, use_container_width=True)  # Display the figure within the column
def query_transportation_cost_for_supplier_and_warehouse(G, supplier_id, warehouse_id):

    if G.has_edge(supplier_id, warehouse_id):
        edge_data = G[supplier_id][warehouse_id]
        st.write(edge_data)
        if edge_data.get("relationship_type") == "SUPPLIERSToWAREHOUSE":
            return edge_data.get("transportation_cost")
    return None


def create_graph():
    # Define node attributes
    nodes = {
        "SUPPLIERS": [
            "node_type", "name", "location", "reliability", "size", 
            "size_category", "supplied_part_types", "id"
        ],
        "WAREHOUSE": [
            "node_type", "name", "type", "location", "size_category",
            "max_capacity", "current_capacity", "safety_stock", "max_parts", 
            "capacity", "id"
        ],
        "PARTS": [
            "node_type", "name", "type", "subtype", "cost", 
            "importance_factor", "valid_from", "valid_till", "id"
        ],
        "PRODUCT_OFFERING": [
            "node_type", "name", "cost", "demand", "id"
        ],
    }

    # Define edge attributes
    edges = {
        "SUPPLIERSToWAREHOUSE": [
            "relationship_type", "transportation_cost", "lead_time", 
            "source", "target"
        ],
        "WAREHOUSEToPARTS": [
            "relationship_type", "inventory_level", "storage_cost", 
            "source", "target"
        ],
        "WAREHOUSEToPRODUCT_OFFERING": [
            "relationship_type", "inventory_level", "storage_cost", 
            "source", "target"
        ]
    }

    # Create a new figure
    fig = go.Figure()

    # Define node positions
    positions = {
        "SUPPLIERS": (0.25,0.1),         # Top-left
        "WAREHOUSE": (-0.1, -0.1),             # Center
        "PARTS": (0.2, -0.2),            # Bottom-right
        "PRODUCT_OFFERING": (-0.05, 0.2),  # Top-right
    }

    # Add edges
    fig.add_trace(go.Scatter(
        x=[positions["SUPPLIERS"][0], positions["WAREHOUSE"][0]],
        y=[positions["SUPPLIERS"][1], positions["WAREHOUSE"][1]],
        mode='lines', line=dict(width=2, color='white'),
        hoverinfo='text',
        text=['<b>SUPPLIERSToWAREHOUSE</b><br>' + '<br>'.join(edges["SUPPLIERSToWAREHOUSE"])]
    ))

    fig.add_trace(go.Scatter(
        x=[positions["WAREHOUSE"][0], positions["PARTS"][0]],
        y=[positions["WAREHOUSE"][1], positions["PARTS"][1]],
        mode='lines', line=dict(width=2, color='white'),
        hoverinfo='text',
        text=['<b>WAREHOUSEToPARTS</b><br>' + '<br>'.join(edges["WAREHOUSEToPARTS"])]
    ))

    fig.add_trace(go.Scatter(
        x=[positions["WAREHOUSE"][0], positions["PRODUCT_OFFERING"][0]],
        y=[positions["WAREHOUSE"][1], positions["PRODUCT_OFFERING"][1]],
        mode='lines', line=dict(width=2, color='white'),
        hoverinfo='text',
        text=['<b>WAREHOUSEToPRODUCT_OFFERING</b><br>' + '<br>'.join(edges["WAREHOUSEToPRODUCT_OFFERING"])]
    ))

    # Add nodes
    for node, (x, y) in positions.items():
        fig.add_trace(go.Scatter(
            x=[x], y=[y], mode='markers+text',
            marker=dict(size=15, color={
                'SUPPLIERS': 'blue', 'WAREHOUSE': 'orange', 
                'PARTS': 'green', 'PRODUCT_OFFERING': 'cyan'}[node]),
            text=[node], textposition='top center', hoverinfo='text',
            hovertext=f'<b>{node}</b><br>' + '<br>'.join(nodes[node])
        ))

    # Update layout
    fig.update_layout(
        title=dict(
            text="Warehouse Schema",
            x=0.5, xanchor='center', yanchor='top',y=0.92
        ),
        height=450,
        width=400,  # Further reduced width for compact layout
        margin=dict(l=10, r=10, t=30, b=10),  # Minimized margins
        xaxis=dict(
            showgrid=False, zeroline=False, showticklabels=False,
            range=[-0.3, 0.4]  # Tightened x-axis range
        ),
        yaxis=dict(
            showgrid=False, zeroline=False, showticklabels=False,
            range=[-0.3, 0.3]  # Tightened y-axis range
        ),
        showlegend=False,
        font=dict(color="white", size=10),
        hoverlabel=dict(bgcolor="black", font_color="white"),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )

    return fig

# @st.fragment
# def node_details_input(warehouse_nodes):
#     col1,col2=st.columns([2,1])
#     with col1:
#         # Heading for the Business Group Info
#         st.write("### Warehouse Information Viewer")
#         all_warehouses = ["Select Warehouse"]
#         for warehouse in warehouse_nodes:
#             all_warehouses.append(warehouse[-1])


#         warehouse_id = st.selectbox("Choose Business Id",all_warehouses)
    
#     if warehouse_id!="Select Warehouse":
#         node_details(warehouse_nodes, warehouse_id)


@st.fragment
def node_details_input():

    col1, col2 = st.columns([1.5, 1],gap="large")
    with col2:
        st.write("###")
        timestamp = st.slider("Select Timestamp", min_value=0, max_value=len(st.session_state.temporal_graph.files) - 1)
    with col1:
        war_index = st.session_state.temporal_graph.create_node_type_index(timestamp)["WAREHOUSE"]
        # Heading for the Business Group Info
        st.write("### Warehouse Information Viewer")
        
        # Use the keys of the index dictionary directly
        all_war = ["Select Warehouse"] + list(war_index.keys())

        # Create a selectbox using these keys
        war_id_input = st.selectbox("Choose Warehouse Id",all_war)
    # Display node details if a valid business group is selected
    if war_id_input!="Select Warehouse":
        node_details(war_index, war_id_input,timestamp)

@st.fragment
@time_and_memory_streamlit
def node_details(node_index, war_id,timestamp):
    col1, col2 = st.columns(2)
    with col1:
        st.write("### Warehouse Info")
        
        # Fetch details directly from the index dictionary
        node_data = node_index.get(war_id)
        
        if node_data:
            attributes = [
            ("Node Type", "🏗"),
            ("Name", "📛"),
            ("Type", "⚙"),
            ("Location", "📍"),
            ("Size Category", "📏"),
            ("Max Capacity", "🔢"),
            ("Current Capacity", "📦"),
            ("Safety Stock", "🛡"),
            ("Max Parts", "🔧"),
            ("ID", "🆔")
            ]
            st.markdown("""
            <style>
                .warehouse-table {
                    width: 100%;
                    margin-top: 20px;
                    border-collapse: collapse;
                    font-size: 16px;
                    font-family: Arial, sans-serif;
                }
                .warehouse-table td {
                    padding: 8px 12px;
                }
                .warehouse-table td:first-child {
                    font-weight: bold;
                    color: #0d47a1; /* Blue color for attribute labels */
                    width: 40%;
                    text-align: left;
                }
                .warehouse-table td:last-child {
                    color: #2596be; /* Gray color for attribute values */
                    width: 60%;
                    text-align: left;
                }
            </style>
        """, unsafe_allow_html=True)

            # Ensure node_data is a list and extract values based on their order
            table_rows = ""
            for index, (attr, icon) in enumerate(attributes):
                value = node_data[index] if index < len(node_data) else "N/A"
                table_rows += f"<tr><td>{icon} {attr}:</td><td>{value}</td></tr>"

            st.markdown(
                    f"""
                    <table class="warehouse-table">
                        {table_rows}
                    </table>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.warning("Warehouse ID not found.")

    with col2:
        # if found:
        graph=st.session_state.temporal_graph.load_graph_at_timestamp(timestamp)
        ego_graph = ego_graph_query(graph, war_id, 1)
        if ego_graph:
            st.write(f"### Neighbors for {war_id}")
            # st.write(f"Ego Graph for Node: {supplier_id}")
            # st.write(f"Nodes: {ego_graph.number_of_nodes()}, Edges: {ego_graph.number_of_edges()}")

            # Visualize and render the ego graph with Plotly
            fig = plotly_ego_graph(ego_graph)
            st.plotly_chart(fig)  # Display the figure in Streamlit


# @st.fragment
# @time_and_memory_streamlit
# def node_details(warehouse_nodes, warehouse_id):
#     col1, col2 = st.columns(2)
#     with col1:
#         # Heading for the Warehouse Info
#         st.write("### Warehouse Info")

#         attributes = [
#             ("Node Type", "🏗"),
#             ("Name", "📛"),
#             ("Type", "⚙"),
#             ("Location", "📍"),
#             ("Size Category", "📏"),
#             ("Max Capacity", "🔢"),
#             ("Current Capacity", "📦"),
#             ("Safety Stock", "🛡"),
#             ("Max Parts", "🔧"),
#             ("ID", "🆔")
#         ]

#         # Style for the no-border table
#         st.markdown("""
#             <style>
#                 .warehouse-table {
#                     width: 100%;
#                     margin-top: 20px;
#                     border-collapse: collapse;
#                     font-size: 16px;
#                     font-family: Arial, sans-serif;
#                 }
#                 .warehouse-table td {
#                     padding: 8px 12px;
#                 }
#                 .warehouse-table td:first-child {
#                     font-weight: bold;
#                     color: #0d47a1; /* Blue color for attribute labels */
#                     width: 40%;
#                     text-align: left;
#                 }
#                 .warehouse-table td:last-child {
#                     color: #2596be; /* Gray color for attribute values */
#                     width: 60%;
#                     text-align: left;
#                 }
#             </style>
#         """, unsafe_allow_html=True)

#         found = False

#         # Loop through warehouse data to find matching Warehouse ID and display details
#         for val in warehouse_nodes:  # Replace with your actual warehouse data source
#             if warehouse_id and warehouse_id in val:
#                 found = True

#                 # Create a no-border table for displaying attributes and values
#                 table_rows = ""
#                 for attr, icon in attributes:
#                     # Extract values dynamically based on attributes
#                     table_rows += f"<tr><td>{icon} {attr}:</td><td>{val[attributes.index((attr, icon))]}</td></tr>"

#                 # Display the table
#                 st.markdown(
#                     f"""
#                     <table class="warehouse-table">
#                         {table_rows}
#                     </table>
#                     """,
#                     unsafe_allow_html=True
#                 )

#         if not found:
#             st.warning('Enter a valid Warehouse ID')
#     with col2:
#         if found:
#             graph=st.session_state.temporal_graph.load_graph_at_timestamp(1)
#             ego_graph = ego_graph_query(graph, warehouse_id, 1)
#             if ego_graph:
#                 st.write(f"### Neighbors for {warehouse_id}")
#                 # st.write(f"Ego Graph for Node: {supplier_id}")
#                 # st.write(f"Nodes: {ego_graph.number_of_nodes()}, Edges: {ego_graph.number_of_edges()}")

#                 # Visualize and render the ego graph with Plotly
#                 fig = plotly_ego_graph(ego_graph)
#                 st.plotly_chart(fig)  # Display the figure in Streamlit




def donut_chart(data, title="Warehouse-size Distribution"):

    labels = list(data.keys())
    values = list(data.values())

    # Define custom colors for the chart
    colors = ['#636EFA', '#EF553B', '#00CC96']  # Blue, Red, Green

    # Create the donut chart
    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.6,  # Creates a more pronounced donut effect
                hoverinfo="label+percent+value",
                textinfo="label+percent",
                textfont=dict(size=15),
                marker=dict(colors=colors, line=dict(color='#FFFFFF', width=2)),  # Add white borders
                pull=[0.1, 0, 0.1],  # Slightly "pull out" small and large categories
            )
        ]
    )

    # Update layout for better appearance
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,  # Center the title horizontally
            xanchor='center',  # Align title to center
            yanchor='top',  # Align title at the top
            font=dict(size=16),  # Match font size
            y=0.89
        ),
        height=400,  # Set consistent figure height
        margin=dict(l=40, r=40, t=80, b=50),  # Adjust margins
        showlegend=True,
        annotations=[
            dict(
                text="Sizes",
                x=0.5,
                y=0.5,
                font_size=18,
                showarrow=False,
                font_color='gray'
            )
        ]
    )

    return fig


def create_warehouse_map(warehouse_data):

    state_abbreviations = {
        'Washington': 'WA',
        'Florida': 'FL',
        'Georgia': 'GA',
        'Oregon': 'OR',
        'Texas': 'TX',
        'New York': 'NY',
        'Massachusetts': 'MA',
        'California': 'CA',
        'Arizona': 'AZ'
    }
    
    # Convert the data into DataFrames for each warehouse type
    df_dict = {}
    for warehouse_type, places in warehouse_data.items():
        df = pd.DataFrame(places.items(), columns=["State", "Value"])
        df["State_Abbreviation"] = df["State"].map(state_abbreviations)
        df_dict[warehouse_type] = df

    # Create traces for each warehouse type
    traces = {}
    for warehouse_type, df in df_dict.items():
        traces[warehouse_type] = go.Choropleth(
            locations=df["State_Abbreviation"],
            z=df["Value"],
            locationmode="USA-states",
            colorscale="Blues",
            colorbar_title="Count",
            hoverinfo="location+z+text",
            text=df["State"]  # Hover text
        )

    # Create the figure
    fig = go.Figure()

    # Add traces for each warehouse type (initially hidden except 'supplier')
    for warehouse_type, trace in traces.items():
        visible = True if warehouse_type == "supplier" else False
        fig.add_trace(trace)
        fig.data[-1].visible = visible

    # Add radio buttons to toggle between traces
    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                buttons=[
                    dict(
                        label="Supplier",
                        method="update",
                        args=[
                            {"visible": [True if t == "supplier" else False for t in traces]},
                            {"title": "Concentration of Supplier Warehouses"}
                        ]
                    ),
                    dict(
                        label="Subassembly",
                        method="update",
                        args=[
                            {"visible": [True if t == "subassembly" else False for t in traces]},
                            {"title": "Concentration of Subassemblies Warehouses"}
                        ],
                    ),
                    dict(
                        label="LAM",
                        method="update",
                        args=[
                            {"visible": [True if t == "lam" else False for t in traces]},
                            {"title": "Concentration of LAMs Warehouses"}
                        ]
                    )
                ],
                x=0.5,
                y=1.1,
                xanchor="center",
                yanchor="top",
                showactive=True,
                bgcolor="rgba(88, 84, 86, 0.8)",
                
                font=dict(
                    color="rgba(14,17,23,255)",  # Text color
                    size=17,  # Font size
                    family="Arial, sans-serif",  # Font family
                    weight="bold"  # Bold title
                )
                
            )
        ],
        geo=dict(
            scope="usa",
            showlakes=True,
            lakecolor="rgb(255,255,255)"
        ),
        title=dict(
        text='Concentration of Warehouses',
        x=0.5,
        y=0.915,
        xanchor='center',
        yanchor='top'
        ),
        template="plotly_dark"
    )

    return fig

def check_units_available_in_warehouse(graph, product_id):
    for node in graph.nodes(data=True):
        if node[0] == product_id:
            product_id_node = node
            break

    in_edges = graph.in_edges(product_id_node[0], data=True)
    available = {}

    for source, target, edge_data in in_edges:
        if edge_data["relationship_type"] == "WAREHOUSEToPRODUCT_OFFERING" and target == product_id:
            if source not in available:
                available[source] = 0

            available[source] += edge_data["inventory_level"]

    # Prepare the output as a sentence
    if available:
        warehouse_info = []
        for warehouse, inventory in available.items():
            warehouse_info.append(f"{warehouse}: {round(inventory)} units")
        warehouse_list = ", ".join(warehouse_info)
        return f"The following warehouses have the product with ID '{product_id}' available: {warehouse_list}."
    else:
        return f"No warehouses found with the product with ID '{product_id}'."

def find_suppliers_to_warehouse_table(graph, warehouse_id):
    supplier_data = []

    in_edges = graph.in_edges(warehouse_id, data=True)

    for source, target, edge_data in in_edges:
        if edge_data["relationship_type"] == "SUPPLIERSToWAREHOUSE" and target == warehouse_id:
            supplier_name = graph.nodes[source].get("name", source)  # Supplier node's name
            part_types = graph.nodes[source].get("supplied_part_types", [])  # Extract supplied part types
            
            # Ensure part_types is a valid list
            if isinstance(part_types, list) and part_types:
                part_list = ", ".join(part_types)  # Convert list to comma-separated string
            else:
                part_list = "Unknown"
            
            supplier_data.append({"Supplier": supplier_name, "Supplied Parts": part_list})

    # Convert the data into a Pandas DataFrame
    suppliers_df = pd.DataFrame(supplier_data)

    return suppliers_df


def find_parts_for_warehouse(graph, warehouse_id):
    # Data storage for parts
    parts_data = []

    # Iterate through out-edges of the warehouse node
    out_edges = graph.out_edges(warehouse_id, data=True)
    
    for source, target, edge_data in out_edges:
        if edge_data.get("relationship_type") == "WAREHOUSEToPARTS":
            part_name = graph.nodes[target].get("name", target)  # Get part name
            part_type = graph.nodes[target].get("type", "Unknown")  # Get part type
            inventory_level = edge_data.get("inventory_level", "Unknown")  # Inventory level from edge data
            storage_cost = edge_data.get("storage_cost", "Unknown")  # Storage cost from edge data
            
            # Append part details
            parts_data.append({
                "Part Name": part_name,
                "Part Type": part_type,
                "Inventory Level": inventory_level,
                "Storage Cost": storage_cost
            })

    # Convert to DataFrame for structured output
    parts_df = pd.DataFrame(parts_data)
    return parts_df

#max-capacity-current capacity should be greater than 15 percent of max-capacity
def find_warehouses_below_safety_stock(graph):
    under_threshold_warehouses = []

    for node, data in graph.nodes(data=True):
        if data.get("node_type") == "WAREHOUSE":
            max_capacity = data.get("max_capacity", 0)
            current_capacity = data.get("current_capacity", 0)
            # Check if max_capacity - current_capacity is less than or equal to 15% of max_capacity
            if max_capacity > 0 and (max_capacity - current_capacity) <= 0.15 * max_capacity:
                under_threshold_warehouses.append({
                    "Warehouse Name": data.get("name", node),
                    "Max Capacity": max_capacity,
                    "Current Capacity": current_capacity,
                    "Location": data.get("location", "Unknown"),
                })

    warehouse_df = pd.DataFrame(under_threshold_warehouses)
    return warehouse_df

def find_warehouses_by_storage_cost(graph):
    warehouse_cost_data = []

    for node, data in graph.nodes(data=True):
        if data.get("node_type") == "WAREHOUSE":
            total_storage_cost = 0
            out_edges = graph.out_edges(node, data=True)
            for source, target, edge_data in out_edges:
                if edge_data.get("relationship_type") == "WAREHOUSEToPARTS":
                    total_storage_cost += edge_data.get("storage_cost", 0)

            warehouse_cost_data.append({
                "Warehouse Name": data.get("name", node),
                "Total Storage Cost": total_storage_cost,
                "Location": data.get("location", "Unknown"),
            })

    warehouse_df = pd.DataFrame(warehouse_cost_data).sort_values(by="Total Storage Cost", ascending=True)
    return warehouse_df

def queries():
    st.title("Queries")
    timestamp = 2
    graph = st.session_state.temporal_graph.load_graph_at_timestamp(timestamp)
    query_option = st.selectbox("Choose Query", ["Select", "Check available units","Find Suppliers Supplying to a Warehouse",
                                                 "Find Parts in Warehouse", "Find Warehouses Below Safety Stock",
                                                 "Find Warehouses by Storage Cost"])
    if query_option=="Check available units":
        po_ids = get_product_offering_ids(graph)
        if po_ids:
            po_ids = st.selectbox(
                "Select PRODUCT OFFERING ID",
                options=po_ids,
                format_func=lambda x: f"{x}",
            )
        else:
            st.warning("No Product Offering IDs available for the selected timestamp.")
            return
        if st.button("Check Availability"):
            avail=check_units_available_in_warehouse(graph, po_ids)
            st.success(avail)
    
    elif query_option == "Find Suppliers Supplying to a Warehouse":
        warehouse_ids = [node for node, data in graph.nodes(data=True) if data.get("node_type") == "WAREHOUSE"]
        selected_warehouse = st.selectbox("Select a Warehouse ID:", warehouse_ids)

        if st.button("Find suppliers"):
            result = find_suppliers_to_warehouse_table(graph, selected_warehouse)
            
            # Display the result as a table
            if not result.empty:
                st.table(result)  # Use st.table to display the Pandas DataFrame as a static table
            else:
                st.write("No suppliers found for the selected warehouse.")
    
    elif query_option == "Find Parts in Warehouse":
        warehouse_ids = [node for node, data in graph.nodes(data=True) if data.get("node_type") == "WAREHOUSE"]

        if warehouse_ids:
            selected_warehouse = st.selectbox("Select a Warehouse ID:", warehouse_ids)

            if st.button("Find Parts"):
                result = find_parts_for_warehouse(graph, selected_warehouse)
                
                if result.empty:
                    st.warning(f"No parts found for the warehouse '{selected_warehouse}'.")
                else:
                    st.dataframe(result)
        else:
            st.error("No warehouse nodes found in the graph.")

    elif query_option == "Find Warehouses Below Safety Stock":
        if st.button("Find Warehouses"):
                
            result = find_warehouses_below_safety_stock(graph)
            st.dataframe(result)

    elif query_option == "Find Warehouses by Storage Cost":
        if st.button("Find Warehouses"):
            result = find_warehouses_by_storage_cost(graph)
            st.dataframe(result)


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

    st.title("Warehouse Dashboard")

    if "temporal_graph" not in st.session_state:
        st.error("No Temporal Graph found in the session state. Please run the main script first.")
        return
    
    static_part()
    
    st.divider() 
    
    node_details_input()
    
    st.text(" ")  # Adds one blank line
    st.text(" ")  # Adds another blank line

    st.divider() 

    queries()
    

if __name__ == "__main__":
    main()