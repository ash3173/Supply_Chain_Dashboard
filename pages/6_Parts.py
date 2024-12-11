import streamlit as st
from datetime import datetime
from collections import Counter
from collections import defaultdict
import requests
import plotly.graph_objects as go
import pandas as pd
import altair as alt
import networkx as nx
import pandas as pd
import plotly.express as px

from utils import time_and_memory_streamlit, plotly_ego_graph, ego_graph_query

# st.set_page_config(
#     layout="wide",
#     initial_sidebar_state="expanded",
#     )

def static_part():
    timestamp = 0
    data = st.session_state.temporal_graph.load_json_at_timestamp(timestamp)

    
    type = {
        "raw" : 0,
        "subassembly" : 0
    }

    parts_nodes=data["node_values"]["PARTS"]
    raw = defaultdict(int)
    subassembly = defaultdict(int)

    for i in parts_nodes :
        type[i[2]] += 1

        if i[2] == "raw" :
            raw[i[3]] += 1
        else :
            subassembly[i[3]] += 1
    
    cols0,cols1,cols2,cols3 = st.columns([1,1,1,1.5])

    with cols0 :
        fig = create_graph()
        st.plotly_chart(fig, use_container_width=True)

    with cols1 :
        fig = create_bar(raw,"Raw Materials")
        st.plotly_chart(fig)

    with cols2:
        fig = create_bar(subassembly,"Subassembly Materials")
        st.plotly_chart(fig)

    with cols3 :
        fig = donut_chart(type)
        st.plotly_chart(fig)
def create_graph():
    # Define node attributes
    nodes = {
        "WAREHOUSE": ["node_type", "name", "type", "location", "size_category", "max_capacity", "current_capacity", "safety_stock", "max_parts", "id"],
        "FACILITY": ["node_type", "name", "type", "location", "max_capacity", "operating_cost", "id"],
        "PARTS": ["node_type", "name", "type", "subtype", "cost", "importance_factor", "valid_from", "valid_till", "id"]
    }

    # Define edge attributes
    edges = {
        "WAREHOUSEToPARTS": ["relationship_type", "inventory_level", "storage_cost", "source", "target"],
        "FACILITYToPARTS": ["relationship_type", "production_cost", "lead_time", "quantity", "source", "target"],
        "PARTSToFACILITY": ["relationship_type", "quantity", "distance", "transport_cost", "lead_time", "source", "target"]
    }

    # Create a new figure
    fig = go.Figure()

    # Define node positions with more separation
    positions = {
        "WAREHOUSE": (0, 0.2),  # Left-center
        "FACILITY": (0, -0.3),  # Left-center (same x as WAREHOUSE but different y for vertical separation)
        "PARTS": (1, 0)  # Right-center
    }

    # Add edges
    fig.add_trace(go.Scatter(
        x=[positions["WAREHOUSE"][0], positions["PARTS"][0]],
        y=[positions["WAREHOUSE"][1], positions["PARTS"][1]],
        mode='lines', line=dict(width=2, color='white'),
        hoverinfo='text',
        text=['<b>WAREHOUSEToPARTS</b><br>' + '<br>'.join(edges["WAREHOUSEToPARTS"])]
    ))

    fig.add_trace(go.Scatter(
        x=[positions["FACILITY"][0], positions["PARTS"][0]],
        y=[positions["FACILITY"][1], positions["PARTS"][1]],
        mode='lines', line=dict(width=2, color='white'),
        hoverinfo='text',
        text=['<b>FACILITYToPARTS</b><br>' + '<br>'.join(edges["FACILITYToPARTS"])]
    ))

    fig.add_trace(go.Scatter(
        x=[positions["PARTS"][0], positions["FACILITY"][0]],
        y=[positions["PARTS"][1], positions["FACILITY"][1]],
        mode='lines', line=dict(width=2, color='white'),
        hoverinfo='text',
        text=['<b>PARTSToFACILITY</b><br>' + '<br>'.join(edges["PARTSToFACILITY"])]
    ))

    # Add nodes
    for node, (x, y) in positions.items():
        fig.add_trace(go.Scatter(
            x=[x], y=[y], mode='markers+text',
            marker=dict(size=15, color={'WAREHOUSE': 'blue', 'FACILITY': 'orange', 'PARTS': 'green'}[node]),
            text=[node], textposition='top center', hoverinfo='text',
            hovertext=f'<b>{node}</b><br>' + '<br>'.join(nodes[node])
        ))

    # Update layout
    fig.update_layout(
        title=dict(
            text="Parts Schema",
            x=0.5, xanchor='center', yanchor='top',y=0.88
        ),
        height=400,
        width=500,  # Adjust width for a tighter fit
        margin=dict(l=20, r=20, t=40, b=20),  # Minimized margins
        xaxis=dict(
            showgrid=False, zeroline=False, showticklabels=False,
            range=[-0.2, 1.2]  # Adjust x-axis range to fit nodes snugly
        ),
        yaxis=dict(
            showgrid=False, zeroline=False, showticklabels=False,
            range=[-0.6, 0.6]  # Adjust y-axis range to fit nodes snugly
        ),
        showlegend=False,
        font=dict(color="white", size=10),
        hoverlabel=dict(bgcolor="black", font_color="white"),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )

    return fig


@st.fragment
def node_details_input():

    col1, col2 = st.columns([1.5, 1],gap="large")
    with col2:
        st.write("###")
        timestamp = st.slider("Select Timestamp", min_value=0, max_value=len(st.session_state.temporal_graph.files) - 1)
    with col1:
        
        parts_index = st.session_state.temporal_graph.create_node_type_index(timestamp)["PARTS"]
        # Heading for the Business Group Info
        st.write("### Parts Information Viewer")
        
        # Use the keys of the index dictionary directly
        all_parts = ["Select Part"] + list(parts_index.keys())

        # Create a selectbox using these keys
        parts_id_input = st.selectbox("Choose Parts Id",all_parts)
    # Display node details if a valid business group is selected
    if parts_id_input!="Select Part":
        node_details(parts_index, parts_id_input,timestamp)


@st.fragment
@time_and_memory_streamlit
def node_details(node_index, part_id,timestamp):
    col1, col2 = st.columns(2)
    with col1:
        st.write("### Part Info")
        
        # Fetch details directly from the index dictionary
        node_data = node_index.get(part_id)
        
        if node_data:
            attributes = [
            ("Node Type", "🔗"),
            ("Name", "📛"),
            ("Type", "🔧"),
            ("Subtype", "🔩"),
            ("Cost", "💰"),
            ("Importance Factor", "⭐"),
            ("Valid From", "📅"),
            ("Valid Till", "📆"),
            ("ID", "🆔")
            ]
            st.markdown("""
            <style>
                .part-table {
                    width: 100%;
                    margin-top: 20px;
                    border-collapse: collapse;
                    font-size: 16px;
                    font-family: Arial, sans-serif;
                }
                .part-table td {
                    padding: 8px 12px;
                }
                .part-table td:first-child {
                    font-weight: bold;
                    color: #0d47a1; /* Blue color for attribute labels */
                    width: 40%;
                    text-align: left;
                }
                .part-table td:last-child {
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
                    <table class="part-table">
                        {table_rows}
                    </table>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.warning("Part ID not found.")

    with col2:
        # if found:
        graph=st.session_state.temporal_graph.load_graph_at_timestamp(timestamp)
        ego_graph = ego_graph_query(graph, part_id, 1)
        if ego_graph:
            st.write(f"### Neighbors for {part_id}")
            # st.write(f"Ego Graph for Node: {supplier_id}")
            # st.write(f"Nodes: {ego_graph.number_of_nodes()}, Edges: {ego_graph.number_of_edges()}")

            # Visualize and render the ego graph with Plotly
            fig = plotly_ego_graph(ego_graph)
            st.plotly_chart(fig)  # Display the figure in Streamlit

def donut_chart(data, title="Raw Material Distribution"):
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
                pull=[0.1 if v == max(values) else 0 for v in values],  # Pull only the largest segment
            )
        ]
    )

    # Update layout for consistent styling with bar chart
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
        margin=dict(l=80, r=40, t=80, b=50),  # Adjust margins
        font=dict(
            family="Arial, sans-serif",  # Consistent font
            size=14,  # Label font size
            color="white"  # Use black text
        ),
        annotations=[
            dict(
                text="Sizes",  # Inner circle text
                x=0.5,
                y=0.5,
                font=dict(size=16, color='white'),  # Match annotation styling
                showarrow=False,
            )
        ]
    )

    return fig


# Add decorator for time and memory tracking (Assuming the time_and_memory decorator is implemented elsewhere)
# from some_module import time_and_memory
def query_valid_parts_nx(timestamp, start_date: str, end_date: str):

    try:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError as e:
        st.error(f"Error parsing dates: {e}")
        return []

    # Load the graph at the given timestamp
    graph = st.session_state.temporal_graph.load_graph_at_timestamp(timestamp)
    
    # List to store valid parts (node IDs) and their valid_till dates
    valid_parts_details = []
    
    # Iterate through the nodes in the graph
    for node, attributes in graph.nodes(data=True):
        # Extract valid_from and valid_till, with default empty string if not present
        valid_from_str = attributes.get('valid_from', '')
        valid_till_str = attributes.get('valid_till', '')
        
        # Only process valid nodes with valid dates
        if valid_from_str and valid_till_str:
            try:
                valid_from = datetime.strptime(valid_from_str, "%Y-%m-%d")
                valid_till = datetime.strptime(valid_till_str, "%Y-%m-%d")
                
                if valid_from <= end_date and valid_till >= start_date:
                    valid_parts_details.append({
                        'part_id': node,
                        'valid_till': valid_till.strftime("%Y-%m-%d")
                    })
            except ValueError:
                # Handle any invalid date format gracefully
                st.warning(f"Skipping node {node} due to invalid date format.")
                continue
    
    # Display the results in a container in Streamlit
    if valid_parts_details:
        with st.container(height=300):
            st.write(f"Found {len(valid_parts_details)} valid parts within the date range:")
            for part in valid_parts_details:
                st.write(f"Part ID: {part['part_id']} is  valid till {part['valid_till']}")
    else:
        st.write("No valid parts found for the given date range.")

    return valid_parts_details

def query_most_common_subtypes_nx(timestamp: int, n: int)->str:
    # Load the graph at the given timestamp
    graph = st.session_state.temporal_graph.load_graph_at_timestamp(timestamp)

    # List to store subtypes
    subtypes = []

    # Iterate through the nodes in the graph and extract the 'subtype' from the node attributes
    for node, attributes in graph.nodes(data=True):
        subtype = attributes.get('subtype', None)
        if subtype:
            subtypes.append(subtype)

    # Use Counter to count occurrences of each subtype
    subtype_counts = Counter(subtypes)

    # Get the n most common subtypes
    most_common_subtypes = subtype_counts.most_common(n)

    if most_common_subtypes:
        result_table = pd.DataFrame(most_common_subtypes, columns=["Subtype", "Occurrences"])
    else:
        result_table = pd.DataFrame(columns=["Subtype", "Occurrences"])  # Return an empty DataFrame

    return result_table

# Bottleneck analysis for parts
# @time_and_memory
def bottleneck_parts_temporal(timestamp, importance_threshold, expected_life_threshold):
    
    # Load the graph for the specified timestamp
    graph = st.session_state.temporal_graph.load_graph_at_timestamp(timestamp)
    
    bottlenecks = []
    
    # Iterate through nodes to find parts
    for node, data in graph.nodes(data=True):
        if data.get("node_type") == "PARTS":
            importance = data.get("importance_factor", 0)
            valid_from = data.get("valid_from", "1970-01-01")
            valid_till = data.get("valid_till", "9999-12-31")

            # Parse valid_from and valid_till as datetime objects
            try:
                valid_from_date = datetime.strptime(valid_from, "%Y-%m-%d")
                valid_till_date = datetime.strptime(valid_till, "%Y-%m-%d")
                expected_life = (valid_till_date - valid_from_date).days
            except ValueError:
                expected_life = float('inf')  # Handle invalid dates gracefully

            # Check if part qualifies as a bottleneck
            if importance >= importance_threshold and expected_life <= expected_life_threshold:
                bottlenecks.append({
                    "Node ID": node,
                    "Importance Factor": importance,
                    "Expected Life (days)": expected_life
                })
    
    # Convert the results to a DataFrame
    return pd.DataFrame(bottlenecks)

# # Query suppliers for part via warehouse
# @time_and_memory
def query_suppliers_for_part_via_warehouse(timestamp, part_id):
    
    G = st.session_state.temporal_graph.load_graph_at_timestamp(timestamp)

    if part_id not in G:
        return f"Part with ID '{part_id}' not found in the graph."
    suppliers = []

    # Traverse edges originating from the given part to find facilities
    for facility_node in G.predecessors(part_id):
        facility_data = G.nodes[facility_node]
        if facility_data.get("node_type") == "WAREHOUSE":
            # Traverse edges originating from the facility to find suppliers
            for supplier_node in G.predecessors(facility_node):
                supplier_data = G.nodes[supplier_node]
                if supplier_data.get("node_type") == "SUPPLIERS":
                    suppliers.append({
                        "Supplier ID": supplier_node,
                        # "Name": supplier_data.get("name"),
                        "Location": supplier_data.get("location"),
                        # "Reliability": supplier_data.get("reliability"),
                        # "Size": supplier_data.get("size"),
                        # "Size Category": supplier_data.get("size_category"),
                        # "Supplied Part Types": supplier_data.get("supplied_part_types")
                    })

    if not suppliers:
        return f"No suppliers found for part with ID '{part_id}'."

    df = pd.DataFrame(suppliers)

    # Display the DataFrame in Streamlit as a table
    # st.table(df)

    return df

# Query: Distance Impact on Costs


def parts_with_larger_distances_and_lower_costs(timestamp, min_distance, max_transport_cost):
    
    # Load graph at the given timestamp
    G = st.session_state.temporal_graph.load_graph_at_timestamp(timestamp)
    
    results = []

    # Iterate over all PARTS nodes
    for node, data in G.nodes(data=True):
        if data.get("node_type") == "PARTS":
            part_id = node  # Get the Part ID
            # Traverse all neighbors connected by PARTSToFACILITY relationship
            for neighbor, edge_data in G[node].items():
                if edge_data.get("relationship_type") == "PARTSToFACILITY":
                    facility_id = neighbor  # The connected facility ID
                    distance = edge_data.get("distance", 0)
                    transport_cost = edge_data.get("transport_cost", 0)

                    # Check if the edge meets the criteria
                    if distance >= min_distance and transport_cost <= max_transport_cost:
                        results.append({
                            "Part ID": part_id,
                            "Facility ID": facility_id,
                            "Distance": distance,
                            "Transport Cost": transport_cost
                        })

    # Convert results to a DataFrame and sort by distance in descending order
    results_df = pd.DataFrame(results)
    if not results_df.empty:
        results_df = results_df.sort_values(by="Distance", ascending=False)

    return results_df


def create_bar(mydict,title):
    df = pd.DataFrame.from_dict(mydict, orient='index', columns=['Frequency'])
    df = df.reset_index().rename(columns={'index': 'Parts'})
    fig2 = px.bar(df, x='Parts', y='Frequency', title=title)
    fig2.update_traces(marker_color='#ADD8E6')

    # Center the title
    fig2.update_layout(
        title=dict(
            text=title,
            x=0.5,  # Center the title
            xanchor='center',  # Align to center horizontally
            yanchor='top'  # Align vertically at the top
        ),
        height=370,
        
    )
    return fig2


@st.fragment
def queries():
    col1, col2=st.columns([2,1])
    with col1:
        timestamp=1
        st.write("### Queries based on Parts")
        query_option = st.selectbox("Choose Query", ["Select","Valid Parts Query", "Most Common Subtypes Query", 
                                                            "Bottleneck Parts Analysis", "Suppliers for Part", 
                                                            "Parts with Larger Distances and Lower Costs"])

        # Perform the query based on selected option
        if query_option == "Valid Parts Query":
            # Date input for the query
            start_date = st.date_input("Start Date", value=datetime(2024, 1, 1))
            end_date = st.date_input("End Date", value=datetime(2026, 12, 31))

            # Convert to string format
            start_date_str = start_date.strftime("%Y-%m-%d")
            end_date_str = end_date.strftime("%Y-%m-%d")

            if st.button("Run Valid Parts Query"):
                # with st.container(height=500):
                #     valid_parts = 
                query_valid_parts_nx(timestamp, start_date_str, end_date_str)
                    # if valid_parts:
                    #     st.write("Found valid parts:")
                    #     for part in valid_parts:
                    #         st.write(f"The Part ID {part['part_id']} is Valid Till: {part['valid_till']}")
                    # else:
                    #     st.write("No valid parts found for the given date range.")

        elif query_option == "Most Common Subtypes Query":
            n = st.number_input("Number of most common subtypes", min_value=1, max_value=10, value=5)

            if st.button("Run Most Common Subtypes Query"):
                # common_subtypes = query_most_common_subtypes_nx(timestamp, n)
                # with st.container():
                result_table = query_most_common_subtypes_nx(timestamp, n)
                if result_table.empty:
                    st.write(f"No subtypes found at timestamp {timestamp}.")
                else:
                    st.write(f"The {n} most common subtypes at timestamp {timestamp} are:")
                    st.table(result_table)

        elif query_option == "Bottleneck Parts Analysis":
            importance_threshold = st.slider("Importance Threshold", min_value=0.0, max_value=1.0, value=0.5)
            expected_life_threshold = st.slider("Expected Life Threshold (days)", min_value=0, max_value=1000, value=500)

            if st.button("Run Bottleneck Parts Query"):
            # Run the query and display results in a container
            # with st.container():
                bottleneck_table = bottleneck_parts_temporal(timestamp, importance_threshold, expected_life_threshold)
                if bottleneck_table.empty:
                    st.write("No bottleneck parts found for the given criteria.")
                else:
                    st.write(f"Bottleneck Parts at Timestamp {timestamp}:")
                    st.table(bottleneck_table)  # Display the DataFrame as a table


        elif query_option == "Suppliers for Part":
            part_ids = st.session_state.temporal_graph.create_node_type_index(timestamp)["PARTS"].keys()
            if part_ids:
                part_ids = st.selectbox(
                    "Select PART ID",
                    options=part_ids,
                    format_func=lambda x: f"{x}",
                )
            else:
                st.warning("No PART IDs available for the selected timestamp.")
                return
            if st.button("Run Suppliers Query"):
                suppliers = query_suppliers_for_part_via_warehouse(timestamp, part_ids)
                st.write(f"Suppliers for part {part_ids}:", suppliers)

        elif query_option == "Parts with Larger Distances and Lower Costs":
            min_distance = st.number_input("Minimum Distance", value=100.0, step=10.0)
            max_transport_cost = st.number_input("Maximum Transport Cost", value=50.0, step=5.0)

            if st.button("Run Query"):
                results_df = parts_with_larger_distances_and_lower_costs(timestamp, min_distance, max_transport_cost)

                if not results_df.empty:
                    st.write("Parts with larger distances and lower transport costs:")
                    st.table(results_df)
                else:
                    st.write("No parts found matching the criteria.")
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
    st.title("Parts Dashboard")
    if "temporal_graph" not in st.session_state:
        st.error("No Temporal Graph found in the session state. Please run the main script first.")
        return

    static_part()
    
    st.divider() 

    # node_details_input(parts_nodes)
    node_details_input()
    st.divider() 

    queries()

    st.text(" ")  # Adds one blank line
    st.text(" ")  # Adds another blank line

    st.divider() 
 


if __name__ == "__main__":
    main()
