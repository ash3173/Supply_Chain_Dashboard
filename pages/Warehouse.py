import streamlit as st
import json
import plotly.graph_objects as go

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
        "SUPPLIERS": ["node_type", "name", "location", "reliability", "size", "size_category", "supplied_part_types", "id"],
        "WAREHOUSE": ["node_type", "name", "type", "location", "size_category", "max_capacity", "current_capacity", "safety_stock", "max_parts", "capacity", "id"],
        "PARTS": ["node_type", "name", "type", "subtype", "cost", "importance_factor", "valid_from", "valid_till", "id"],
        "PRODUCT_OFFERING": ["node_type", "name", "cost", "demand", "id"]
    }

    # Define edge attributes
    edges = {
        "SUPPLIERSToWAREHOUSE": ["relationship_type", "transportation_cost", "lead_time", "source", "target"],
        "WAREHOUSEToPARTS": ["relationship_type", "inventory_level", "storage_cost", "source", "target"],
        "WAREHOUSEToPRODUCT_OFFERING": ["relationship_type", "inventory_level", "storage_cost", "source", "target"]
    }

    # Create a new figure
    fig = go.Figure()

    # Add edge: SUPPLIERS to WAREHOUSE
    fig.add_trace(go.Scatter(
        x=[0, 0.33], y=[0, -0.3], mode='lines', line=dict(width=2, color='white'),
        hoverinfo='text',
        text=['<b>SUPPLIERSToWAREHOUSE</b><br>' + '<br>'.join(edges["SUPPLIERSToWAREHOUSE"])]
    ))

    # Add edge: WAREHOUSE to PARTS
    fig.add_trace(go.Scatter(
        x=[0.33, 0.66], y=[-0.3, -0.6], mode='lines', line=dict(width=2, color='white'),
        hoverinfo='text',
        text=['<b>WAREHOUSEToPARTS</b><br>' + '<br>'.join(edges["WAREHOUSEToPARTS"])]
    ))

    # Add edge: WAREHOUSE to PRODUCT_OFFERING
    fig.add_trace(go.Scatter(
        x=[0.33, 1], y=[-0.3, -0.6], mode='lines', line=dict(width=2, color='white'),
        hoverinfo='text',
        text=['<b>WAREHOUSEToPRODUCT_OFFERING</b><br>' + '<br>'.join(edges["WAREHOUSEToPRODUCT_OFFERING"])]
    ))

    # Add SUPPLIERS node
    fig.add_trace(go.Scatter(
        x=[0], y=[0], mode='markers+text', marker=dict(size=15, color='cyan'),
        text=['SUPPLIERS'], textposition='top center', hoverinfo='text',
        hovertext='<b>SUPPLIERS</b><br>' + '<br>'.join(nodes["SUPPLIERS"])
    ))

    # Add WAREHOUSE node
    fig.add_trace(go.Scatter(
        x=[0.33], y=[-0.3], mode='markers+text', marker=dict(size=15, color='orange'),
        text=['WAREHOUSE'], textposition='top center', hoverinfo='text',
        hovertext='<b>WAREHOUSE</b><br>' + '<br>'.join(nodes["WAREHOUSE"])
    ))

    # Add PARTS node
    fig.add_trace(go.Scatter(
        x=[0.66], y=[-0.6], mode='markers+text', marker=dict(size=15, color='green'),
        text=['PARTS'], textposition='top center', hoverinfo='text',
        hovertext='<b>PARTS</b><br>' + '<br>'.join(nodes["PARTS"])
    ))

    # Add PRODUCT_OFFERING node
    fig.add_trace(go.Scatter(
        x=[1], y=[-0.6], mode='markers+text', marker=dict(size=15, color='blue'),
        text=['PRODUCT_OFFERING'], textposition='top center', hoverinfo='text',
        hovertext='<b>PRODUCT_OFFERING</b><br>' + '<br>'.join(nodes["PRODUCT_OFFERING"])
    ))

    # Update layout for visibility
    fig.update_layout(
        title=dict(
            text="Supply Chain Schema",
            x=0, xanchor='left', yanchor='top'
        ),
        height=500,
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis=dict(
            showgrid=False, zeroline=False, showticklabels=False,
            range=[-0.2, 1.2]  # Adjust x-axis range for padding
        ),
        yaxis=dict(
            showgrid=False, zeroline=False, showticklabels=False,
            range=[-0.8, 0.2]  # Adjust y-axis range for padding
        ),
        showlegend=False,
        font=dict(color="white", size=10),
        hoverlabel=dict(bgcolor="black", font_color="white"),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
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
    

    st.title("Querying Transportation Cost for Supplier and Warehouse")
    
    # Load the JSON data at the given timestamp
    # with open(st.session_state.temporal_graph.files[timestamp], 'r') as f:
    #     temporal_graph = json.load(f)

    # all_suppliers = []
    # for supplier_data in temporal_graph["node_values"]["Supplier"] :
    #     all_suppliers.append(supplier_data[-1])

    # all_warehouses = []
    # for warehouse_data in temporal_graph["node_values"]["Warehouse"] :
    #     all_warehouses.append(warehouse_data[-1])

    graph = st.session_state.temporal_graph.load_graph_at_timestamp(timestamp)
    all_suppliers = []
    all_warehouses = []
    for node_id, node_data in graph.nodes(data=True):
        if node_data.get("node_type") == "SUPPLIERS":
            all_suppliers.append(node_id)
        elif node_data.get("node_type") == "WAREHOUSE":
            all_warehouses.append(node_id)

    supplier_id = st.sidebar.selectbox("Select Supplier ID:", options=all_suppliers)
    warehouse_id = st.sidebar.selectbox("Select Warehouse ID:", options=all_warehouses)

    transportation_cost = query_transportation_cost_for_supplier_and_warehouse(graph, supplier_id, warehouse_id)
    if transportation_cost is None:
        st.write("No transportation cost found for the given Supplier and Warehouse.")
    else :
        st.write("Transportation cost:",transportation_cost)    
    
if __name__ == "__main__":
    main()