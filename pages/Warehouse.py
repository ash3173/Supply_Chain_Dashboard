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

@st.fragment
def node_details_input(warehouse_nodes):
    col1,col2=st.columns([2,1])
    with col1:
        # Heading for the Business Group Info
        st.write("### Warehouse Information Viewer")
        all_warehouses = ["Select Warehouse"]
        for warehouse in warehouse_nodes:
            all_warehouses.append(warehouse[-1])


        warehouse_id = st.selectbox("Choose Business Id",all_warehouses)
    
    if warehouse_id!="Select Warehouse":
        node_details(warehouse_nodes, warehouse_id)

@st.fragment
@time_and_memory_streamlit
def node_details(warehouse_nodes, warehouse_id):
    col1, col2 = st.columns(2)
    with col1:
        # Heading for the Warehouse Info
        st.write("### Warehouse Info")

        attributes = [
            ("Node Type", "🏗️"),
            ("Name", "📛"),
            ("Type", "⚙️"),
            ("Location", "📍"),
            ("Size Category", "📏"),
            ("Max Capacity", "🔢"),
            ("Current Capacity", "📦"),
            ("Safety Stock", "🛡️"),
            ("Max Parts", "🔧"),
            ("ID", "🆔")
        ]

        # Style for the no-border table
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

        found = False

        # Loop through warehouse data to find matching Warehouse ID and display details
        for val in warehouse_nodes:  # Replace with your actual warehouse data source
            if warehouse_id and warehouse_id in val:
                found = True

                # Create a no-border table for displaying attributes and values
                table_rows = ""
                for attr, icon in attributes:
                    # Extract values dynamically based on attributes
                    table_rows += f"<tr><td>{icon} {attr}:</td><td>{val[attributes.index((attr, icon))]}</td></tr>"

                # Display the table
                st.markdown(
                    f"""
                    <table class="warehouse-table">
                        {table_rows}
                    </table>
                    """,
                    unsafe_allow_html=True
                )

        if not found:
            st.warning('Enter a valid Warehouse ID')
    with col2:
        if found:
            graph=st.session_state.temporal_graph.load_graph_at_timestamp(1)
            ego_graph = ego_graph_query(graph, warehouse_id, 1)
            if ego_graph:
                st.write(f"### Neighbors for {warehouse_id}")
                # st.write(f"Ego Graph for Node: {supplier_id}")
                # st.write(f"Nodes: {ego_graph.number_of_nodes()}, Edges: {ego_graph.number_of_edges()}")

                # Visualize and render the ego graph with Plotly
                fig = plotly_ego_graph(ego_graph)
                st.plotly_chart(fig)  # Display the figure in Streamlit





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
    
    timestamp = 2
    
    url_data = requests.get(st.session_state.temporal_graph.files[timestamp])
    if url_data.status_code != 200:
        st.error("Failed to load data from the server.")
        return
    data = url_data.json()
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
    
    st.divider() 
    
    node_details_input(warehouse_nodes)
    
    st.text(" ")  # Adds one blank line
    st.text(" ")  # Adds another blank line

    st.divider() 
    
    # Load the JSON data at the given timestamp
    # with open(st.session_state.temporal_graph.files[timestamp], 'r') as f:
    #     temporal_graph = json.load(f)

    # all_suppliers = []
    # for supplier_data in temporal_graph["node_values"]["Supplier"] :
    #     all_suppliers.append(supplier_data[-1])

    # all_warehouses = []
    # for warehouse_data in temporal_graph["node_values"]["Warehouse"] :
    #     all_warehouses.append(warehouse_data[-1])

    # graph = st.session_state.temporal_graph.load_graph_at_timestamp(timestamp)
    # all_suppliers = []
    # all_warehouses = []
    # for node_id, node_data in graph.nodes(data=True):
    #     if node_data.get("node_type") == "SUPPLIERS":
    #         all_suppliers.append(node_id)
    #     elif node_data.get("node_type") == "WAREHOUSE":
    #         all_warehouses.append(node_id)

    # supplier_id = st.sidebar.selectbox("Select Supplier ID:", options=all_suppliers)
    # warehouse_id = st.sidebar.selectbox("Select Warehouse ID:", options=all_warehouses)

    # transportation_cost = query_transportation_cost_for_supplier_and_warehouse(graph, supplier_id, warehouse_id)
    # if transportation_cost is None:
    #     st.write("No transportation cost found for the given Supplier and Warehouse.")
    # else :
    #     st.write("Transportation cost:",transportation_cost)    
    



#     9. Temporal Clustering of Nodes/Edges
# Query: "Group nodes or edges into clusters based on attribute similarity over timestamps."

# Purpose: Find clusters of nodes or edges (e.g., Warehouses with similar current_capacity trends) over time.
# Example Output: Temporal cluster maps.
if __name__ == "__main__":
    main()