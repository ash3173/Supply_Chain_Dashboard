import streamlit as st
import json
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import requests
import networkx as nx

from utils import time_and_memory_streamlit, plotly_ego_graph, ego_graph_query

st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
    )

def static_part():
    timestamp = 1

    # Load the JSON data at the given timestamp
    # with open(st.session_state.temporal_graph.files[timestamp], 'r') as f:
    #     data = json.load(f)
    # url_data = requests.get(st.session_state.temporal_graph.files[timestamp])
    # if url_data.status_code != 200:
    #     st.error("Failed to load data from the server.")
    #     return
    # data = url_data.json()
    data = st.session_state.temporal_graph.load_json_at_timestamp(timestamp)

    col1, col2, col3 = st.columns([1,4,1.5], gap='medium')

    with col1:
        fig = create_graph()
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig1, fig2,supplier_data = get_visualization(data)
        st.plotly_chart(fig1, use_container_width=True)  # Display figure 1

    with col3:
        st.plotly_chart(fig2, use_container_width=True)  # Display figure 2
# Define the function to query lead time
@time_and_memory_streamlit
def query_lead_time_supplier_to_warehouse(G, timestamp, supplier_id, warehouse_id):
    if G.has_edge(supplier_id, warehouse_id):
        edge_data = G[supplier_id][warehouse_id]
        if edge_data.get("relationship_type") == "SUPPLIERSToWAREHOUSE":
            lead_time = edge_data.get("lead_time")
            return lead_time
        else:
            return None
    else:
        return None

@time_and_memory_streamlit
def supplier_reliability_costing_temporal(graph, timestamp, reliability_threshold, max_transportation_cost):
    """
    Analyze supplier reliability and transportation costs at a specific timestamp in a temporal graph.

    Parameters:
        graph (Graph): The temporal graph object for the specified timestamp.
        timestamp (int): The specific timestamp to analyze.
        reliability_threshold (float): The minimum acceptable reliability threshold for suppliers.
        max_transportation_cost (float): The maximum acceptable transportation cost.

    Returns:
        list: A list of suppliers meeting the criteria, including supplier ID, reliability, and transportation cost.
    """
    suppliers = []

    # Iterate through edges and check if they belong to SUPPLIERSToWAREHOUSE relationship
    for u, v, data in graph.edges(data=True):
        # Check if the edge type matches SUPPLIERSToWAREHOUSE
        if data.get("relationship_type") == "SUPPLIERSToWAREHOUSE":
            transportation_cost = data.get("transportation_cost", 0)
            
            # Check if the transportation cost is within the acceptable range
            if transportation_cost <= max_transportation_cost:
                # Extract and check the reliability of the supplier node
                reliability = graph.nodes[u].get("reliability", 0)
                if reliability >= reliability_threshold:
                    suppliers.append((u, reliability, transportation_cost))

    return suppliers

# @st.fragment
# def node_details_input(supplier_data):
#     col1,col2=st.columns([2,1])
#     with col1:
#         st.write("### Supplier Details Viewer")
#         all_supplier = ["Select Suppliers"]
#         for supp in supplier_data:
#             all_supplier.append(supp[-1])
#         supplier_id_input = st.selectbox("Choose Supplier Id",all_supplier)
    
#     if supplier_id_input!="Select Suppliers":
#         node_details(supplier_data, supplier_id_input)

@st.fragment
def node_details_input():

    col1, col2 = st.columns([1.5, 1],gap="large")
    with col2:
        st.write("###")
        timestamp = st.slider("Select Timestamp", min_value=0, max_value=len(st.session_state.temporal_graph.files) - 1)
    with col1:
        
        sup_index = st.session_state.temporal_graph.create_node_type_index(timestamp)["SUPPLIERS"]
        # Heading for the Business Group Info
        st.write("### Supplier Information Viewer")
        
        # Use the keys of the index dictionary directly
        all_supp = ["Select Supplier"] + list(sup_index.keys())

        # Create a selectbox using these keys
        sup_id_input = st.selectbox("Choose Supplier Id",all_supp)
    # Display node details if a valid business group is selected
    if sup_id_input!="Select Supplier":
        node_details(sup_index, sup_id_input,timestamp)

@st.fragment
@time_and_memory_streamlit
def node_details(node_index, sup_id,timestamp):
    col1, col2 = st.columns(2)
    with col1:
        st.write("### Supplier Info")
        
        # Fetch details directly from the index dictionary
        node_data = node_index.get(sup_id)
        
        if node_data:
            attributes = [
            ("Node Type", "🔗"),
            ("Name", "📛"),
            ("Location", "📍"),
            ("Reliability", "📊"),
            ("Size", "📐"),
            ("Size Category", "📦"),
            ("Supplied Part Types", "🛠️"),
            ("ID", "🆔")
            ]
            
            st.markdown("""
            <style>
                .supplier-table {
                    width: 100%;
                    margin-top: 20px;
                    border-collapse: collapse;
                    font-size: 16px;
                    font-family: Arial, sans-serif;
                }
                .supplier-table td {
                    padding: 8px 12px;
                }
                .supplier-table td:first-child {
                    font-weight: bold;
                    color: #0d47a1; /* Blue color for attribute labels */
                    width: 40%;
                    text-align: left;
                }
                .supplier-table td:last-child {
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
                    <table class="supplier-table">
                        {table_rows}
                    </table>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.warning("Supplier ID not found.")

    with col2:
        # if found:
        graph=st.session_state.temporal_graph.load_graph_at_timestamp(timestamp)
        ego_graph = ego_graph_query(graph, sup_id, 1)
        if ego_graph:
            st.write(f"### Neighbors for {sup_id}")
            # st.write(f"Ego Graph for Node: {supplier_id}")
            # st.write(f"Nodes: {ego_graph.number_of_nodes()}, Edges: {ego_graph.number_of_edges()}")

            # Visualize and render the ego graph with Plotly
            fig = plotly_ego_graph(ego_graph)
            st.plotly_chart(fig)  # Display the figure in Streamlit




# @st.fragment
# @time_and_memory_streamlit
# def node_details(supplier_data,supplier_id):
#     col1, col2=st.columns(2)


#     with col1:
#         st.write("### Supplier Info")
    
#                 # Define the attributes of the supplier
#         attributes = [
#             ("Node Type", "🔗"),
#             ("Name", "📛"),
#             ("Location", "📍"),
#             ("Reliability", "📊"),
#             ("Size", "📐"),
#             ("Size Category", "📦"),
#             ("Supplied Part Types", "🛠️"),
#             ("ID", "🆔")
#         ]

#         # Style for the no-border table
#         st.markdown("""
#             <style>
#                 .supplier-table {
#                     width: 100%;
#                     margin-top: 20px;
#                     border-collapse: collapse;
#                     font-size: 16px;
#                     font-family: Arial, sans-serif;
#                 }
#                 .supplier-table td {
#                     padding: 8px 12px;
#                 }
#                 .supplier-table td:first-child {
#                     font-weight: bold;
#                     color: #0d47a1; /* Blue color for attribute labels */
#                     width: 40%;
#                     text-align: left;
#                 }
#                 .supplier-table td:last-child {
#                     color: #2596be; /* Gray color for attribute values */
#                     width: 60%;
#                     text-align: left;
#                 }
#             </style>
#         """, unsafe_allow_html=True)

#         found = False

#         # Loop through supplier data to find matching Supplier ID and display details
#         for val in supplier_data:
#             if supplier_id and supplier_id in val:
#                 found = True

#                 # Create a no-border table for displaying attributes and values
#                 table_rows = ""
#                 for attr, icon in attributes:
#                     if attr == "Supplied Part Types":
#                         # Convert the list of supplied parts to a comma-separated string
#                         part_types = ", ".join(val[6])
#                         table_rows += f"<tr><td>{icon} {attr}:</td><td>{part_types}</td></tr>"
#                     else:
#                         table_rows += f"<tr><td>{icon} {attr}:</td><td>{val[attributes.index((attr, icon))]}</td></tr>"

#                 # Display the table
#                 st.markdown(
#                     f"""
#                     <table class="supplier-table">
#                         {table_rows}
#                     </table>
#                     """,
#                     unsafe_allow_html=True
#                 )

#         if not found:
#             st.warning('Enter a valid supplier ID')
            
    
    
#     with col2:
#         if found:
#             graph=st.session_state.temporal_graph.load_graph_at_timestamp(1)
#             ego_graph = ego_graph_query(graph, supplier_id, 1)
#             if ego_graph:
#                 st.write(f"### Neighbors for {supplier_id}")
#                 # st.write(f"Ego Graph for Node: {supplier_id}")
#                 # st.write(f"Nodes: {ego_graph.number_of_nodes()}, Edges: {ego_graph.number_of_edges()}")

#                 # Visualize and render the ego graph with Plotly
#                 fig = plotly_ego_graph(ego_graph)
#                 st.plotly_chart(fig)  # Display the figure in Streamlit

@st.fragment
def queries():
    col1, col2=st.columns([2,1])
    with col1:
        timestamp=1
        graph=st.session_state.temporal_graph.load_graph_at_timestamp(timestamp)
        # Heading for the Supplier ID Info
        st.write("### Queries based on Suppliers")

        query_type = st.selectbox("Choose Query", ["Select","Supplier Reliability and Costing Analysis", "Given a Supplier ID and Warehouse ID get lead time."])

        if query_type == "Supplier Reliability and Costing Analysis":
            st.info("Suppliers with high reliability and low transportation cost")
            reliability_threshold = st.slider("Reliability Threshold", min_value=0.0, max_value=1.0, value=0.95, step=0.01)
            max_transportation_cost = st.number_input("Max Transportation Cost", min_value=0.0, value=50.0, step=0.1)
            
            results = supplier_reliability_costing_temporal(graph, timestamp, reliability_threshold, max_transportation_cost)
            
            with st.container(height=300):
        
                if results:
                    st.write("### Suppliers meeting the criteria:")
                    for supplier in results:
                        st.write(f"Supplier ID: {supplier[0]}, Reliability: {supplier[1]:.2f}, Transportation Cost: {supplier[2]:.2f}")
                else:
                    st.write("No suppliers meet the specified criteria.")

        elif query_type=="Given a Supplier ID and Warehouse ID get lead time.":
            supplier_id = st.text_input("Enter Supplier ID", "S_003")
            warehouse_id = st.text_input("Enter Warehouse ID", "W_143")

            lead_time = query_lead_time_supplier_to_warehouse(graph, timestamp, supplier_id, warehouse_id)

            if lead_time is not None:
                st.success(f"Lead time between Supplier {supplier_id} and Warehouse {warehouse_id}: {lead_time}")
            else:
                st.error(f"No relationship or lead time data found between Supplier {supplier_id} and Warehouse {warehouse_id}.")

def get_visualization(data):
    supplier_data = data["node_values"]["SUPPLIERS"]
    place_freq = {}
    items_freq = {}

    for i in supplier_data:
        place = i[2]
        if place in place_freq:
            place_freq[place] += 1
        else:
            place_freq[place] = 1

        for items in i[6]:
            if items in items_freq:
                items_freq[items] += 1
            else:
                items_freq[items] = 1

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

    # Create a DataFrame and add state abbreviations
    df = pd.DataFrame(place_freq.items(), columns=['State', 'Value'])
    df['State_Abbreviation'] = df['State'].map(state_abbreviations)

    # Create the choropleth map
    fig1 = px.choropleth(
        df,
        locations='State_Abbreviation',  # Use abbreviations
        locationmode="USA-states",       # Use USA states mode
        color='Value',                   # Column to determine color
        scope="usa",                     # Focus on USA
        color_continuous_scale="Blues",  # Color scale
        labels={'Value': 'Supplier Count'}, # Customize label
        title='Concentration of Suppliers'

    )

    # Update layout for better appearance
    fig1.update_layout(
    template='plotly_dark',
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    title=dict(
        text='Concentration of Suppliers',
        x=0.5,
        xanchor='center',
        yanchor='top'
    ),
    geo=dict(
        showlakes=True,
        lakecolor='rgb(255, 255, 255)'
    )
    )

    # Create the bar chart with blue color
    df = pd.DataFrame.from_dict(items_freq, orient='index', columns=['Frequency'])
    df = df.reset_index().rename(columns={'index': 'Item'})
    fig2 = px.bar(df, x='Item', y='Frequency', title='Number of suppliers per item')
    fig2.update_traces(marker_color='#ADD8E6')

    # Center the title
    fig2.update_layout(
        title=dict(
            text='Number of suppliers per item',
            x=0.5,  # Center the title
            xanchor='center',  # Align to center horizontally
            yanchor='top'  # Align vertically at the top
        )
    )

    return [fig1, fig2,supplier_data]



def create_graph():
    # Define node attributes for Supplier and Warehouse
    nodes = {
        'Supplier': ['node_type', 'name', 'location', 'reliability', 'size', 'size_category', 'supplied_part_types', 'id'],
        'Warehouse': ['node_type', 'name', 'type', 'location', 'size_category', 'max_capacity', 'current_capacity', 'safety_stock', 'max_parts', 'id']
    }
    edge = ['relationship_type', 'transportation_cost', 'lead_time', 'source', 'target']

    # Create a new figure
    fig = go.Figure()

    # Add edge (Supplier to Warehouse) - vertically aligned
    fig.add_trace(go.Scatter(
        x=[0, 1], y=[0, -1], mode='lines', line=dict(width=2, color='white'),
        hoverinfo='text',
        text=['<b>Edge Attributes</b><br>' + '<br>'.join(edge)]  # Edge hover text formatted line-by-line
    ))

    # Add Supplier node (positioned at y=0)
    fig.add_trace(go.Scatter(
        x=[0], y=[0], mode='markers+text', marker=dict(size=20, color='cyan'),
        text=['Supplier'], textposition='top center', hoverinfo='text',
        hovertext='<b>Supplier</b><br>' + '<br>'.join(nodes['Supplier'])  # Show only attribute names
    ))

    # Add Warehouse node (positioned at y=-1)
    fig.add_trace(go.Scatter(
        x=[1], y=[-1], mode='markers+text', marker=dict(size=20, color='orange'),
        text=['Warehouse'], textposition='top center', hoverinfo='text',
        hovertext='<b>Warehouse</b><br>' + '<br>'.join(nodes['Warehouse'])  # Show only attribute names
    ))

    # Update layout for dark mode, transparent background, and properly formatted hover text
    fig.update_layout(
        title=dict(
        text="Supplier Schema",  # Title text
        x=0.5,  # Center the title
        xanchor='center',  # Horizontal alignment
        yanchor='top'  # Vertical alignment
    ),  showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        font=dict(color="white"),  # White text color
        hoverlabel=dict(bgcolor="black", font_color="white"),  # Hover label styling
        plot_bgcolor='rgba(0,0,0,0)',  # Transparent background
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent paper background
    )

    return fig

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
    

    st.title("Supplier Dashboard")
    if "temporal_graph" not in st.session_state:
        st.error("No Temporal Graph found in the session state. Please run the main script first.")
        return

    static_part()

    st.divider() 
    
    node_details_input()
    
    
    st.divider() 
    queries()
    st.text(" ")  # Adds one blank line
    st.text(" ")  # Adds another blank line

    st.divider()  # Adds a horizontal divider (thin line), visually separating sections

if __name__ == "__main__":
    main()