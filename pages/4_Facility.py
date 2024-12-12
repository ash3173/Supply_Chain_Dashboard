import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import time
import tracemalloc
import functools
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import networkx as nx
from utils import time_and_memory_streamlit,ego_graph_query,plotly_ego_graph

# st.set_page_config(
#     layout="wide",
#     initial_sidebar_state="expanded",
#     )

@st.fragment
def static_part():
    timestamp=0
    # url_data = requests.get(st.session_state.temporal_graph.files[timestamp])
    # if url_data.status_code != 200:
    #     st.error("Failed to load data from the server.")
    #     return
    # data = url_data.json()
    data = st.session_state.temporal_graph.load_json_at_timestamp(timestamp)

    facility_nodes = data["node_values"]["FACILITY"]
    col1,col2,col3=st.columns([1,4,2])
    with col1:
        fig = create_graph()
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig= create_facility_map(facility_nodes)
        st.plotly_chart(fig, use_container_width=True)  # Display figure 1
    with col3:
        with st.container(border=False): 
            lam_avg_cost, external_avg_cost = compute_average_operating_costs(facility_nodes)
            fig = plot_average_operating_cost(lam_avg_cost, "LAM",external_avg_cost, "External")
            
            st.pyplot(fig)
    st.markdown("<hr style='margin-top: -50px; margin-bottom: -50px; border: none; border-top: 1px solid #ccc;' />", unsafe_allow_html=True)

def create_graph():
    # Define node attributes
    nodes = {
        "PRODUCT_OFFERING": ["node_type", "name", "cost", "demand", "id"],
        "FACILITY": ["node_type", "name", "type", "location", "max_capacity", "operating_cost", "id"],
        "PARTS": ["node_type", "name", "type", "subtype", "cost", "importance_factor", "valid_from", "valid_till", "id"]
    }

    # Define edge attributes
    edges = {
        "FACILITYToPARTS": ["relationship_type", "production_cost", "lead_time", "quantity", "source", "target"],
        "FACILITYToPRODUCT_OFFERING": ["relationship_type", "product_cost", "lead_time", "quantity", "source", "target"],
        "PARTSToFACILITY": ["relationship_type", "quantity", "distance", "transport_cost", "lead_time", "source", "target"]
    }

    # Create a new figure
    fig = go.Figure()

    # Define node positions
    positions = {
        "PRODUCT_OFFERING": (0.5, 0.3),  # Top-center
        "FACILITY": (0, -0.2),          # Center-left
        "PARTS": (1, -0.4)              # Bottom-right
    }

    # Add edges
    fig.add_trace(go.Scatter(
        x=[positions["FACILITY"][0], positions["PARTS"][0]],
        y=[positions["FACILITY"][1], positions["PARTS"][1]],
        mode='lines', line=dict(width=2, color='white'),
        hoverinfo='text',
        text=['<b>FACILITYToPARTS</b><br>' + '<br>'.join(edges["FACILITYToPARTS"])]
    ))

    fig.add_trace(go.Scatter(
        x=[positions["FACILITY"][0], positions["PRODUCT_OFFERING"][0]],
        y=[positions["FACILITY"][1], positions["PRODUCT_OFFERING"][1]],
        mode='lines', line=dict(width=2, color='white'),
        hoverinfo='text',
        text=['<b>FACILITYToPRODUCT_OFFERING</b><br>' + '<br>'.join(edges["FACILITYToPRODUCT_OFFERING"])]
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
            marker=dict(size=15, color={'PRODUCT_OFFERING': 'cyan', 'FACILITY': 'orange', 'PARTS': 'green'}[node]),
            text=[node], textposition='top center', hoverinfo='text',
            hovertext=f'<b>{node}</b><br>' + '<br>'.join(nodes[node])
        ))

    # Update layout
    fig.update_layout(
        title=dict(
            text="Facility Schema",
            x=0.5, xanchor='center', yanchor='top'
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
            range=[-0.6, 0.4]  # Adjust y-axis range to fit nodes snugly
        ),
        showlegend=False,
        font=dict(color="white", size=10),
        hoverlabel=dict(bgcolor="black", font_color="white"),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )

    return fig

def create_facility_map(facility_nodes):
    facility_data = {
        "external": {},
        "lam": {}
    }

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

    for facility in facility_nodes:
        type = facility[2]
        state = facility[3]
        if state not in state_abbreviations:
            print(f"State {state} not found in state_abbreviations")
            continue
        if type not in facility_data:
            print(f"Type {type} not found in facility_data")
            continue
        if state not in facility_data[type]:
            facility_data[type][state] = 0
        facility_data[type][state] += 1

    # Filter out states that are not in the state_abbreviations dictionary
    for facility_type in facility_data:
        facility_data[facility_type] = {state: count for state, count in facility_data[facility_type].items() if state in state_abbreviations}

    # Convert the data into DataFrames for each warehouse type
    df_dict = {}
    for warehouse_type, places in facility_data.items():
        df = pd.DataFrame(places.items(), columns=["State", "Value"])
        df["State_Abbreviation"] = df["State"].map(state_abbreviations)
        df_dict[warehouse_type] = df

    # Create traces for each warehouse type
    traces = {}
    for facility_type, df in df_dict.items():
        traces[facility_type] = go.Choropleth(
            locations=df["State_Abbreviation"],
            z=df["Value"],
            locationmode="USA-states",
            colorscale="Blues",
            colorbar_title="Count",
            text=df["State"],  # Hover text
            marker_line_color='white',  # State boundaries
            marker_line_width=1.5,  # Thin boundary lines
        )

    # Create the figure
    fig = go.Figure()

    # Add traces for each warehouse type (initially hidden except 'lam')
    for facility_type, trace in traces.items():
        visible = True if facility_type == "lam" else False
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
                    label="LAM",
                    method="update",
                    args=[
                        {"visible": [True if t == "lam" else False for t in traces]},
                        {"title": "Concentration of LAM Facilities"}
                    ]
                ),
                dict(
                    label="External",
                    method="update",
                    args=[
                        {"visible": [True if t == "external" else False for t in traces]},
                        {"title": "Concentration of External Facilities"}
                    ]
                )
            ],
            x=0.5,
            y=1.1,
            xanchor="center",
            yanchor="top",
            showactive=True,
            bgcolor="rgba(88, 84, 86, 0.8)",  # Button background color
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
        lakecolor="rgb(255, 255, 255)",
        projection=dict(type="albers usa"),  # Map projection
        center=dict(lat=37.8, lon=-96),  # Center around the USA
        lonaxis_range=[-130, -65],  # Longitudinal limits
        lataxis_range=[23, 50],  # Latitudinal limits
    ),
    title=dict(
        text='Concentration of Facilities',
        x=0.5,
        y=0.95,
        xanchor='center',
        yanchor='top'
    ),
    template="plotly_dark",
    )


    return fig

def compute_average_operating_costs(facilities):

    # Initialize variables to store total operating costs and counts for each type
    lam_total_cost = 0
    lam_count = 0
    external_total_cost = 0
    external_count = 0

    # Iterate through facilities and calculate total costs and counts for each type
    for facility in facilities:
        if facility[2] == 'lam':
            lam_total_cost += facility[5]
            lam_count += 1
        elif facility[2] == 'external':
            external_total_cost += facility[5]
            external_count += 1

    # Calculate average operating costs for each type
    lam_avg_cost = lam_total_cost / lam_count if lam_count != 0 else 0
    external_avg_cost = external_total_cost / external_count if external_count != 0 else 0

    return lam_avg_cost, external_avg_cost


@st.fragment
def node_details_input():

    col1, col2 = st.columns([1.5, 1],gap="large")
    with col2:
        st.write("###")
        timestamp = st.slider("Select Timestamp", min_value=0, max_value=len(st.session_state.temporal_graph.files) - 1)
    with col1:
        
        facility_index = st.session_state.temporal_graph.create_node_type_index(timestamp)["FACILITY"]
        # Heading for the Business Group Info
        st.write("### Facility Information Viewer")
        
        # Use the keys of the index dictionary directly
        all_facility = ["Select Facility"] + list(facility_index.keys())

        # Create a selectbox using these keys
        facility_id_input = st.selectbox("Choose Facility Id",all_facility)
    # Display node details if a valid business group is selected
    if facility_id_input!="Select Facility":
        node_details(facility_index, facility_id_input,timestamp)

@st.fragment
@time_and_memory_streamlit
def node_details(node_index, facility_id,timestamp):
    col1, col2 = st.columns(2)
    with col1:
        st.write("### Facility Info")
        
        # Fetch details directly from the index dictionary
        node_data = node_index.get(facility_id)
        
        if node_data:
            # Define the attributes of the facility
            attributes = [
                ("Node Type", "🔗"),
                ("Name", "📛"),
                ("Type", "🏭"),
                ("Location", "📍"),
                ("Max Capacity", "📦"),
                ("Operating Cost", "💰"),
                ("ID", "🆔")
                ]
            st.markdown("""
            <style>
                .facility-table {
                    width: 100%;
                    margin-top: 20px;
                    border-collapse: collapse;
                    font-size: 16px;
                    font-family: Arial, sans-serif;
                }
                .facility-table td {
                    padding: 8px 12px;
                }
                .facility-table td:first-child {
                    font-weight: bold;
                    color: #0d47a1; /* Blue color for attribute labels */
                    width: 40%;
                    text-align: left;
                }
                .facility-table td:last-child {
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
                    <table class="facility-table">
                        {table_rows}
                    </table>
                    """,
                    unsafe_allow_html=True
                )

        else:
            st.warning("Facility ID not found.")

    with col2:
        # if found:
        graph=st.session_state.temporal_graph.load_graph_at_timestamp(timestamp)
        ego_graph = ego_graph_query(graph, facility_id, 1)
        if ego_graph:
            st.write(f"### Neighbors for {facility_id}")
            # st.write(f"Ego Graph for Node: {supplier_id}")
            # st.write(f"Nodes: {ego_graph.number_of_nodes()}, Edges: {ego_graph.number_of_edges()}")

            # Visualize and render the ego graph with Plotly
            fig = plotly_ego_graph(ego_graph)
            st.plotly_chart(fig)  # Display the figure in Streamlit



def plot_average_operating_cost(operating_cost1, identifier1, operating_cost2, identifier2):
    # Create a figure with two vertically stacked subplots
    fig, axs = plt.subplots(2, 1, figsize=(2, 3), facecolor='none')  # Reduced height
    fig.patch.set_alpha(0)  # Transparent background
    
    for ax, operating_cost, identifier in zip(axs, [operating_cost1, operating_cost2], [identifier1, identifier2]):
        # Set limits for the circular representation
        ax.set_xlim(-1, 1)
        ax.set_ylim(-1, 1)
       
        # Draw a circle in the middle
        circle = Circle((0, 0.5), 0.35, edgecolor='#2596be', facecolor='none', linewidth=3)
        ax.add_artist(circle)
       
        # Add identifier text
        ax.text(
            0, 0.5, identifier, 
            fontsize=8, ha='center', va='center', color='#2596be', weight='bold'
        )
       
        # Add operating cost text
        ax.text(
            0, -0.1, f"Operating Cost Average:\n{operating_cost}", 
            fontsize=7, ha='center', va='center', color='white', weight='bold'
        )
       
        # Hide the axis
        ax.axis('off')

    # Adjust spacing between the plots
    plt.subplots_adjust(hspace=-0.4)  # Reduce the gap between subplots
    
    # Adjust the figure to remove space around the subplots and move everything up
    fig.subplots_adjust(left=0, right=1, top=0.95, bottom=0.05)  # Increase the top margin and reduce the bottom margin to move up


    return fig

@time_and_memory_streamlit
def find_product_offerings_under_threshold(data, threshold_operating_cost):
    product_offerings = []
    highest_operating_cost = 0
    highest_product_offering = None

    for edge in data["link_values"].get("FACILITYToPRODUCT_OFFERING", []):
        source_id = edge[4]  # Facility ID
        target_id = edge[5]  # Product Offering ID

        # Find the corresponding facility and product offering
        facility = next((f for f in data["node_values"]["FACILITY"] if f[6] == source_id), None)
        product = next((p for p in data["node_values"]["PRODUCT_OFFERING"] if p[4] == target_id), None)

        if facility and product:
            operating_cost = facility[5]

            # Add to list if operating cost is below the threshold
            if operating_cost <= threshold_operating_cost:
                product_offerings.append({
                    "Facility Name": facility[1],  # Assuming index 1 is name
                    "Facility Location": facility[3],  # Assuming index 3 is location
                    "Product Name": product[1],  # Assuming index 1 is name
                    "Operating Cost": operating_cost
                })

            # Update the highest operating cost and product offering
            if operating_cost > highest_operating_cost:
                highest_operating_cost = operating_cost
                highest_product_offering = product

    # Convert to Pandas DataFrame for tabular output
    offerings_df = pd.DataFrame(product_offerings)
    offerings_df = offerings_df.sort_values(by='Operating Cost', ascending=False)

    return offerings_df, highest_operating_cost, highest_product_offering


@time_and_memory_streamlit
def find_all_parts_required_in_facility(data):
    facility_to_parts = data["link_values"]["PARTSToFACILITY"]
    facility = {}

    # Collect parts required for each facility
    for edge_data in facility_to_parts:
        if edge_data[-1] not in facility:
            facility[edge_data[-1]] = []

        facility[edge_data[-1]].append(edge_data[-2])

    # Prepare data for the table
    table_data = []
    for facility_name, parts in facility.items():
        parts_list = ", ".join(parts)
        table_data.append([facility_name, parts_list])

    # Create a DataFrame from the table data (optional: if you prefer using pandas)
    
    df = pd.DataFrame(table_data, columns=["Facility", "Parts"])


    st.dataframe(df)
    # Optionally return the dataframe if you need it for further processing
    return df



@time_and_memory_streamlit
def find_facilty_making_product(graph, product_id):
    for node in graph.nodes(data=True):
        if node[0] == product_id:
            product_id_node = node
            break
    in_edges = graph.in_edges(product_id_node[0], data=True)
    facility = {}

    for source, target, edge_data in in_edges:
        if edge_data["relationship_type"] == "FACILITYToPRODUCT_OFFERING" and target == product_id:
            if target not in facility:
                facility[target] = []

            facility[target].append(source)

    if facility:
        facility_list = ", ".join(facility[product_id])
        return f"The facilities making the product with ID '{product_id}' are: {facility_list}."
    else:
        return f"No facilities found making the product with ID '{product_id}'."


@st.fragment
def queries():
    num_timestamps = len(st.session_state.temporal_graph.files)
    st.write("### Facility Queries")
    cols1,cols2=st.columns([2,1],gap="medium")
    with cols2:
        timestamp = st.slider("Select Timestamp", 0, num_timestamps - 1, 0)
    with cols1:
        
        query_option = st.selectbox("Choose Query", ["Select", 
                                                     "Facility with operting cost within a threshold",
                                                    "Parts Present in a facility"
                                                    ,"Facility manufacturing a specfic product"])

        if query_option=="Facility with operting cost within a threshold":

            
            data = st.session_state.temporal_graph.load_json_at_timestamp(timestamp)
            cost_threshold = st.slider("Cost Threshold", min_value=0, max_value=300, value=150)
            if st.button("Find Product Offerings"):
                offerings_df, highest_cost, highest_product = find_product_offerings_under_threshold(data, cost_threshold)

                if not offerings_df.empty:
                    st.write("**Product Offerings Under Threshold**")
                    st.dataframe(offerings_df)

                    st.write("**Highest Operating Cost and Associated Product Offering:**")
                    st.write(f"Operating Cost: {highest_cost}")
                    st.write(f"Product Name: {highest_product[1]}")  # Assuming index 1 is name
                else:
                    st.write("No product offerings found under the given threshold.")

        elif query_option=="Parts Present in a facility":
            
            if st.button("Find Facilities"):
                data = st.session_state.temporal_graph.load_json_at_timestamp(timestamp)
                facility_parts_df = find_all_parts_required_in_facility(data)
                # if not facility_parts_df.empty:
                #     st.table(facility_parts_df)
                # else:
                #     st.warning(f"No facilities found at Timestamp {timestamp}.")
                # # with st.container(height=300):
                # st.write(facility_parts_df)

        elif query_option=="Facility manufacturing a specfic product":
            po_ids = st.session_state.temporal_graph.create_node_type_index(0)["PRODUCT_OFFERING"]
            if po_ids:
                po_ids = st.selectbox(
                    "Select PRODUCT OFFERING ID",
                    options=po_ids.keys(),
                    format_func=lambda x: f"{x}",
                )
            else:
                st.warning("No Product Offering IDs available for the selected timestamp.")
                return
            if st.button("Find Facilities"):
                graph=st.session_state.temporal_graph.load_graph_at_timestamp(timestamp)
                facility_for_prod= find_facilty_making_product(graph,po_ids)
                st.success(facility_for_prod)

    




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
    

    st.title("Facility Dashboard")
    if "temporal_graph" not in st.session_state:
        st.error("No Temporal Graph found in the session state. Please run the main script first.")
        return
    
    static_part()


    node_details_input()

    st.divider()

    queries()
    st.text(" ")  # Adds one blank line
    st.text(" ")  # Adds another blank line

    st.divider()  # Adds a horizontal divider (thin line), visually separating sections
    
if __name__ == "__main__":
    main()