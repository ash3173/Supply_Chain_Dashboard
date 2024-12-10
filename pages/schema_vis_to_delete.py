import streamlit as st
from pyvis.network import Network
import os

def visualize_graph():
    # Initialize PyVis Network with a background color
    net = Network(height='400px', width='100%', directed=True, notebook=False, bgcolor='white', font_color='black')

    # Define node types with attributes
    node_types = {
        "BUSINESS_GROUP": {"color": "#E63946", "size": 20, "properties": "node_type, name, description, revenue, id"},
        "PRODUCT_FAMILY": {"color": "#457B9D", "size": 18, "properties": "node_type, name, revenue, id"},
        "PRODUCT_OFFERING": {"color": "#1D3557", "size": 15, "properties": "node_type, name, cost, demand, id"},
        "SUPPLIERS": {"color": "#2A9D8F", "size": 16, "properties": "node_type, name, location, reliability, size, size_category, supplied_part_types, id"},
        "WAREHOUSE": {"color": "#E9C46A", "size": 17, "properties": "node_type, name, type, location, size_category, max_capacity, current_capacity, safety_stock, max_parts, capacity, id"},
        "FACILITY": {"color": "#F4A261", "size": 17, "properties": "node_type, name, type, location, max_capacity, operating_cost, id"},
        "PARTS": {"color": "#264653", "size": 13, "properties": "node_type, name, type, subtype, cost, importance_factor, valid_from, valid_till, id"},
    }

    # Define relationships
    relationship_types = {
        "BUSINESS_GROUPToPRODUCT_FAMILY": {"color": "#A8DADC", "properties": "relationship_type, source, target"},
        "PRODUCT_FAMILYToPRODUCT_OFFERING": {"color": "#457B9D", "properties": "relationship_type, source, target"},
        "SUPPLIERSToWAREHOUSE": {"color": "#2A9D8F", "properties": "relationship_type, transportation_cost, lead_time, source, target"},
        "WAREHOUSEToPARTS": {"color": "#E9C46A", "properties": "relationship_type, inventory_level, storage_cost, source, target"},
        "WAREHOUSEToPRODUCT_OFFERING": {"color": "#1D3557", "properties": "relationship_type, inventory_level, storage_cost, source, target"},
        "FACILITYToPARTS": {"color": "#F4A261", "properties": "relationship_type, production_cost, lead_time, quantity, source, target"},
        "FACILITYToPRODUCT_OFFERING": {"color": "#264653", "properties": "relationship_type, product_cost, lead_time, quantity, source, target"},
        "PARTSToFACILITY": {"color": "#E63946", "properties": "relationship_type, quantity, distance, transport_cost, lead_time, source, target"},
    }

    # Add nodes
    for node_type, attributes in node_types.items():
        # Format properties for vertical display
        formatted_properties = "\n".join(attributes["properties"].split(", "))
        net.add_node(node_type, label=node_type, color=attributes["color"], size=attributes["size"], title=formatted_properties)

    # Add edges
    for rel_type, attributes in relationship_types.items():
        source, target = rel_type.split("To")
        formatted_properties = "\n".join(attributes["properties"].split(", "))
        net.add_edge(source, target, color=attributes["color"], title=formatted_properties)

    # Save the graph to an HTML file
    net.save_graph("graph_schema.html")

# Streamlit app
st.title("Graph Schema Visualization")

# Visualize the graph
visualize_graph()

# Add custom CSS styling
st.markdown(
    """
    <style>
    iframe {
        background-color: rgba(14,17,23,255);
    }
    body{
        background-color: rgba(14,17,23,255);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Display the HTML file in Streamlit
html_file_path = "graph_schema.html"
if os.path.exists(html_file_path):
    with open(html_file_path, "r") as f:
        html_content = f.read()
    st.components.v1.html(html_content, height=500, width=600)


import streamlit as st
import pandas as pd

# Example data
data = {
    0: [
        "BG_001 (4)",
        "PF_003 (8)",
        "PO_013 (9)",
        "F_001 (10)",
        "P_124 (23)",
        "S_023 (12)",
        "W_039 (26)"
    ]
}
df = pd.DataFrame(data, index=["BusinessGroup", "ProductFamily", "ProductOffering", "Facility", "Parts", "Suppliers", "Warehouse"])

# Block styling
box_style = """
    padding: 20px;
    margin: 10px;
    border-radius: 10px;
    background-color: #264653;
    color: white;
    font-size: 16px;
    text-align: center;
    box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.25);
"""

# Streamlit layout
st.title("Data Visualization - Blocks")
st.subheader("Node Information")

cols = st.columns(2)

with cols[0]:
    # Display each row as a block
    for index, row in df.iterrows():
        st.markdown(
            f"""
            <div style="{box_style}">
                <h3>{index}</h3>
                <p>{row[0]}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
