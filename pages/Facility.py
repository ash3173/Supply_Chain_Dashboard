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
                size=14,  # Font size
                family="Arial",  # Font family
                
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
    template="plotly_dark"
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

def plot_average_operating_cost(operating_cost, identifier):
    # Reduced size of the figure, keeping it proportional
    fig, ax = plt.subplots(figsize=(4, 4), facecolor='none') # Adjusted figsize to reduce size
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
   
    # Draw a circle in the middle
    circle = Circle((0, 0.5), 0.4, edgecolor='#2596be', facecolor='none', linewidth=6)
    ax.add_artist(circle)
   
    # Add identifier text
    ax.text(
        0, 0.5, identifier, 
        fontsize=16, ha='center', va='center', color='#2596be', style='italic', weight='bold'
    )
   
    # Add operating cost text
    ax.text(
        0, -0.2, f"Operating Cost Average:\n{operating_cost}", 
        fontsize=12, ha='center', va='center', color='white', style='italic', weight='bold'
    )

    # Add month text
    # ax.text(
    #     0, -0.4, f"Month: {m}", 
    #     fontsize=10, ha='center', va='center', color='white', style='italic', weight='bold'
    # )    
   
    # Hide the axis
    ax.axis('off')

    # Remove background and extra padding
    fig.patch.set_alpha(0)
   
    # Tight layout to reduce any extra space
    plt.tight_layout(pad=0.1) # Minimized padding

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
    

    st.title("Facility Dashboard")
    if "temporal_graph" not in st.session_state:
        st.error("No Temporal Graph found in the session state. Please run the main script first.")
        return
    
    timestamp=1
    url_data = requests.get(st.session_state.temporal_graph.files[timestamp])
    if url_data.status_code != 200:
        st.error("Failed to load data from the server.")
        return
    data = url_data.json()

    graph = st.session_state.temporal_graph.load_graph_at_timestamp(timestamp)
    facility_nodes = data["node_values"]["FACILITY"]
    col1,col2,col3=st.columns([1,4,1])
    with col1:
        fig = create_graph()
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig= create_facility_map(facility_nodes)
        st.plotly_chart(fig, use_container_width=True)  # Display figure 1
    with col3:
        lam_avg_cost, external_avg_cost = compute_average_operating_costs(facility_nodes)
        fig_lam = plot_average_operating_cost(lam_avg_cost, "LAM")
        fig_external = plot_average_operating_cost(external_avg_cost, "External")
        st.pyplot(fig_lam)
    with col3:
        st.pyplot(fig_external, use_container_width=True)
if __name__ == "__main__":
    main()