import streamlit as st
import json
import plotly.graph_objects as go
import altair as alt
import requests
import pandas as pd

st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
    )
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
        "SUPPLIERS": (-0.2, 0.2),         # Top-left
        "WAREHOUSE": (0, 0),             # Center
        "PARTS": (0.2, -0.2),            # Bottom-right
        "PRODUCT_OFFERING": (0.3, 0.1),  # Top-right
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
            x=0, xanchor='left', yanchor='top'
        ),
        height=400,
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




def donut_chart(data, title="Warehouse Sizes Distribution"):

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
            x=0.5,  # Center the title
            font=dict(size=20)
        ),
        template="plotly_dark",
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
                # activebgcolor="rgba(60,60,60,1)"
                # bordercolor="white",
                
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