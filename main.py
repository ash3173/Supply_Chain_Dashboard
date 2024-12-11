import streamlit as st
from TemporalGraphClass import TemporalGraphClass
import requests
from dotenv import load_dotenv
import os
import json
import glob
import pandas as pd
import base64
import networkx as nx



st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
    )

# load_dotenv()
# base_url = os.getenv("BASE_URL")
# version = os.getenv("version")
# getVersions = os.getenv("getVersions")
# getdata = f"{base_url}/archive/schema/{version}"
# getTimestamp = f"{base_url}/archive/schema/{version}"

base_url = "http://172.17.149.236/api"
version = "NSS_1000_12_Simulation" 

getVersions = f"{base_url}/versions"
getTimestamp = f"{base_url}/archive/schema/{version}"
getdata = f"{base_url}/archive/schema/{version}"

get_live_data = f"{base_url}/live/schema/{version}"

data_folder = "data"

# Streamlit app starts here
# main for running from server

def check_units_available_in_warehouse(graph,product_id,product_id_node) :

    in_edges = graph.in_edges(product_id_node[0],data=True)
    available = {}

    for source,target,edge_data in in_edges :
        if edge_data["relationship_type"] == "WAREHOUSEToPRODUCT_OFFERING" and target == product_id :
            if source not in available :
                available[source] = 0

            available[source] += edge_data["inventory_level"]

    return available

def find_facilty_making_product(graph,product_id,product_id_node) :
    in_edges = graph.in_edges(product_id_node[0],data=True)
    facility = {}

    for source,target,edge_data in in_edges :
        if edge_data["relationship_type"] == "FACILITYToPRODUCT_OFFERING" and target == product_id :
            if target not in facility :
                facility[target] = []

            facility[product_id].append(source)

    return facility

def find_raw_materials_to_make_product(data,facility) :
    raw_materials = {}
    facility_to_parts = data["link_values"]["FACILITYToPARTS"]
    for edge_data in facility_to_parts :
        if edge_data[-2] == facility :
            raw_materials[edge_data[-1]] = [edge_data[3],edge_data[1],edge_data[2]] # quantity , cost , lead time

    return raw_materials

def find_total_cost(raw_materials,needed_units) :
    for key, values in raw_materials.items():
        raw_materials[key] = [value * needed_units for value in values]

    return raw_materials

def calulate_cost_and_time(total) :
    cost = 0
    time = 0
    for key, values in total.items():
        cost += values[1]
        time += values[2]

    return cost,time

def check_warehouse_have_enough_raw_material(data,raw_materials) :
    warehouse = data["link_values"]["WAREHOUSEToPARTS"]
    all_raw_materials = {}
    for k,v in raw_materials.items() :
        all_raw_materials[k] = v[0]

    for edge_data in warehouse :
        if edge_data[-1] in all_raw_materials :
            all_raw_materials[edge_data[-1]] -= edge_data[3]

    for k,v in raw_materials.items() :
        if v > 0 :
            return False
    
    return True

# need to change
def get_supplier_for_raw_material(data,raw_materials) :
    return "need to change"
    warehouses = data["link_values"]["WAREHOUSEToPARTS"]
    warehouses_containing_raw_materials = []

    for edge_data in warehouses :
        if edge_data[-1] in raw_materials :
            warehouses_containing_raw_materials.append(edge_data[-2])

    suppliers = data["link_values"]["SUPPLIERSToWAREHOUSE"]
    suppliers_for_raw_material = []

    for edge_data in suppliers :
        if edge_data[-2] in warehouses_containing_raw_materials :
            suppliers_for_raw_material.append(edge_data[-1])

    return suppliers_for_raw_material



def supply_chain_query(data,graph,product_id,units,product_id_node) :

    warehouse_containing_product_id = check_units_available_in_warehouse(graph,product_id,product_id_node)
    
    if sum(warehouse_containing_product_id.values()) >= units :
        return [1,warehouse_containing_product_id] # 1 - Demand can be satisfied by warehouse
    
    else :

        available_units = sum(warehouse_containing_product_id.values())
        
        facility = find_facilty_making_product(graph,product_id,product_id_node)
        st.write(facility)

        raw_materials = find_raw_materials_to_make_product(data,facility)
        st.write(raw_materials)

        total_raw_materials = find_total_cost(raw_materials,units - available_units)
        st.write(total_raw_materials)

        check,needed_raw_material = check_warehouse_have_enough_raw_material(data,total_raw_materials)

        if check :
            cost,time = calulate_cost_and_time(total_raw_materials)
            return [2,total_raw_materials,cost,time,units - available_units] # 2 - Demand can be satisfied by making new products
        
        else :
            suppliers = get_supplier_for_raw_material(data,needed_raw_material)
            return [3,suppliers] # 3 - Demand can't be satisfied as not enough parts to make new products


def count_connections_and_find_max_nodes(data):
   connection_counts = {}
  
   # Iterate over all edges in the relationship values
   for type in data["link_values"]:
       for edge in data["link_values"][type]:
           # Determine the relationship type
           relationship_type = edge[0]
           relationship_structure = data["relationship_types"].get(relationship_type, [])
           # st.write(relationship_structure)
       
           # Find the indices for source and target based on the relationship structure
           try:
               source_index = relationship_structure.index("source")
               target_index = relationship_structure.index("target")
           except ValueError:
               continue
           
           # Extract source and target nodes
           source = edge[source_index] if len(edge) > source_index else None
           target = edge[target_index] if len(edge) > target_index else None
       
           # Update connection counts
           if source is not None:
               if source not in connection_counts:
                   connection_counts[source] = {"outgoing": 0, "incoming": 0}
               connection_counts[source]["outgoing"] += 1
           if target is not None:
               if target not in connection_counts:
                   connection_counts[target] = {"outgoing": 0, "incoming": 0}
               connection_counts[target]["incoming"] += 1
   
   # Calculate degree centrality
   degree_centrality = {node: counts["outgoing"] + counts["incoming"]
                       for node, counts in connection_counts.items()}
  
   # Group nodes by type
   grouped_nodes = {
       "BusinessGroup": [],
       "ProductFamily": [],
       "ProductOffering": [],
       "Facility": [],
       "Parts": [],
       "Suppliers": [],
       "Warehouse": []
   }
  
   max_connections_nodes = []
   max_connections = 0
  
   # Group nodes and find max connections
   for node, centrality in degree_centrality.items():
       if node.startswith("BG_"):
           grouped_nodes["BusinessGroup"].append((node, centrality))
       elif node.startswith("PF_"):
           grouped_nodes["ProductFamily"].append((node, centrality))
       elif node.startswith("PO_"):
           grouped_nodes["ProductOffering"].append((node, centrality))
       elif node.startswith("F_"):
           grouped_nodes["Facility"].append((node, centrality))
       elif node.startswith("P_"):
           grouped_nodes["Parts"].append((node, centrality))
       elif node.startswith("S_"):
           grouped_nodes["Suppliers"].append((node, centrality))
       elif node.startswith("W_"):
           grouped_nodes["Warehouse"].append((node, centrality))
          
       if centrality > max_connections:
           max_connections = centrality
           max_connections_nodes = [node]
       elif centrality == max_connections:
           max_connections_nodes.append(node)
  
   # Sort each group by degree centrality
   for group in grouped_nodes:
       grouped_nodes[group].sort(key=lambda x: x[1], reverse=True)
  
   return grouped_nodes, max_connections_nodes, max_connections

def display_node_boxes(df):
    # split cols into 2 , 2 ,3
    col1 , col2 = st.columns(2)
    col3 , col4 = st.columns(2)
    col5 , col6 , col7 = st.columns(3)
    
    # Get first row data
    first_row = df.iloc[0]
    
   
    box_style = """
        margin: 10px;
        padding: 10px;
        border-radius: 5px;
        color: white;
        background: linear-gradient(135deg, #6e8efb, #a777e3);
        border: 1px solid black;
        margin: 5px;
        text-align: center;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        transition: transform 0.2s, box-shadow 0.2s;
        cursor: pointer;
    """

    # Display boxes in the layout
    with col1:
        st.markdown(f"""
            <main style="{box_style}">
                <h4>{first_row['BusinessGroup']}</h4>
                <p>Business Group</p>
            </main>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
            <main style="{box_style}">
                <h4>{first_row['ProductFamily']}</h4>
                <p>Product Family</p>
            </main>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
            <main style="{box_style}">
                <h4>{first_row['ProductOffering']}</h4>
                <p>Product Offering</p>
            </main>
        """, unsafe_allow_html=True)
        
    with col4:
        st.markdown(f"""
            <main style="{box_style}">
                <h4>{first_row['Facility']}</h4>
                <p>Facility</p>
            </main>
        """, unsafe_allow_html=True)
        
    with col5:
        st.markdown(f"""
            <main style="{box_style}">
                <h4>{first_row['Parts']}</h4>
                <p>Parts</p>
            </main>
        """, unsafe_allow_html=True)
        
    with col6:
        st.markdown(f"""
            <main style="{box_style}">
                <h4>{first_row['Suppliers']}</h4>
                <p>Suppliers</p>
            </main>
        """, unsafe_allow_html=True)
        
    with col7:
        st.markdown(f"""
            <main style="{box_style}">
                <h4>{first_row['Warehouse']}</h4>
                <p>Warehouse</p>
            </main>
        """, unsafe_allow_html=True)
  

def convert_json_to_graph(data):
    graph = nx.DiGraph()

    for node_type, nodes in data["node_values"].items():
        for node in nodes:
            node_id = node[-1]
            node_attributes = dict(zip(data["node_types"][node_type], node))
            graph.add_node(node_id, **node_attributes)

    all_edge_types = data["relationship_types"]
    for link_type,link_values in data["link_values"].items():
        for edge_data in link_values :
            attributes = {}
            for j in range(len(edge_data) - 2):
                key = all_edge_types[link_type][j]
                attributes[key] = edge_data[j]
            graph.add_edge(edge_data[-2], edge_data[-1], **attributes)
    
    return graph


def main():
    st.title("Temporal Graph Dashboard")
    # st.write("Selected Version", version)

    # st.write(base_url)

    target_path = os.path.join(data_folder, version)
    if os.path.exists(target_path) and os.path.isdir(target_path):
        pass
        # st.write("Version exists")
        # all_files = [f for f in os.listdir(target_path) if os.path.isfile(os.path.join(target_path, f))]
        # all_timestamps = requests.get(getTimestamp).json()

        # for timestamp in all_timestamps:
        #     if f"{timestamp}.json" not in all_files:
        #         timestamp_data = requests.get(f"{getdata}/{timestamp}").json()
        #         with open(os.path.join(target_path, f"{timestamp}.json"), "w") as f:
        #             json.dump(timestamp_data, f, indent=4)

    else:
        st.write("Version doesnt exist")
        os.makedirs(target_path)
        all_timestamps = requests.get(getTimestamp).json()

        for timestamp in all_timestamps:
            timestamp_data = requests.get(f"{getdata}/{timestamp}").json()
            with open(os.path.join(target_path, f"{timestamp}.json"), "w") as f:
                json.dump(timestamp_data, f, indent=4)

    all_files = [os.path.join(target_path, f) for f in os.listdir(
        target_path) if os.path.isfile(os.path.join(target_path, f))]
    all_files.sort(key=lambda x: int(x.split("\\")[-1].split(".")[0]))
    #all_files.sort(key=lambda x: int(x.split("/")[-1].split(".")[0]))

    # Initialize TemporalGraph
    temporal_graph = TemporalGraphClass(all_files)
    if temporal_graph not in st.session_state:
        st.session_state.temporal_graph = temporal_graph

    # Success message
    st.success("Files processed successfully!")

    st.markdown(
        """
            <style>
            .custom-columns {
                display: flex
                gap: 50px; /* Adjust this value for more or less margin */
            }
            .custom-columns > div {
                flex: 1; /* Ensure equal column width */
            }
            </style>
            <div class="custom-columns">
                <div id="col1"></div>
                <div id="col2"></div>
            </div>
        """,
        unsafe_allow_html=True,
    )

# Use Streamlit's empty container to render content inside custom divs
    col1 , col2 = st.columns(2)

    with col1:
        
        st.write("## Degree Centrality Analysis")
        st.write(" ")
        st.write(" ")
        timestamp = 2
        data = st.session_state.temporal_graph.load_json_at_timestamp(timestamp)
        grouped_nodes, max_connections_nodes, max_connections = count_connections_and_find_max_nodes(data)
    
        # Create DataFrame
        df_data = []
        max_rows = max(len(nodes) for nodes in grouped_nodes.values())
        
        for row in range(max_rows):
            row_data = {}
            for group, nodes in grouped_nodes.items():
                if row < len(nodes):
                    node, centrality = nodes[row]
                    row_data[group] = f"{node}\n({centrality})"
                else:
                    row_data[group] = ""
            df_data.append(row_data)
        
        df = pd.DataFrame(df_data)

        display_node_boxes(df)

    with col2:
        # st.write("## Graph Schema Visualization")
        st.markdown(
            """
            <style>
            .custom-header {
                margin-left: 80px;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        st.markdown('<h2 class="custom-header">Graph Schema Visualization</h2>', unsafe_allow_html=True)


        # Inject custom CSS to style the iframe and make it responsive
        st.markdown(
            """
            <style>
            body {
               margin-left : 10px;
                
            }

            .responsive-iframe {
                width: 100%; /* Full width of the parent container */
                height: 100%; /* Adjust height relative to the parent */
                background-color: rgba(14,17,23,255);
                margin-left : 30px;
                border-radius: 30px;
                border: none;
                overflow: hidden !important; /* Optional: force hide scrollbars */
            }
            .iframe-container {
                width: 100%; /* Parent container width */
                height: 430px; /* Fixed height for the parent container */
                overflow: hidden; /* Hide scrollbars on the container */
                display: flex; /* To ensure iframe fills the container */
                justify-content: center; /* Center iframe */
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        html_file_path = "graph_schema.html"
        if os.path.exists(html_file_path):
            with open(html_file_path, "r") as f:
                html_content = f.read()

            encoded_html = base64.b64encode(html_content.encode("utf-8")).decode("utf-8")

            # Embed the HTML content using base64 encoding
            st.markdown(
                f"""
                <div class="iframe-container">
                    <iframe class="responsive-iframe" src="data:text/html;base64,{encoded_html}"></iframe>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.write("## Supply Chain Query")

    col1 , col2 = st.columns(2)

    with col1:
        
        # get live data
        # data = requests.get(get_live_data).json()
        data = st.session_state.temporal_graph.load_json_at_timestamp(timestamp)

        graph = convert_json_to_graph(data)
        all_products = []
        for po in data["node_values"]["PRODUCT_OFFERING"] :
            all_products.append(po[-1])

        product_id = st.selectbox("Select Product Offering",all_products)
        units = st.number_input("Enter number of units",min_value=1000,max_value=1000000)

        for node in graph.nodes(data=True):
            if node[0] == product_id :
                product_id_node = node
                break
        
        st.write("Product ID Node",product_id_node)
        choice = 0
        if st.button("Check Supply Chain"):
            choice, supply_chain_data = supply_chain_query(data,graph, product_id, units, product_id_node)

    with col2:

        if choice != 0:
            # Handle the different cases returned by the query
            if choice == 1:
                st.write(f"Demand of {units} units can be satisfied.")
                st.write(f"Total available units of {product_id}: {sum(supply_chain_data.values())}")
                
                for warehouse, available_units in supply_chain_data.items():
                    st.write(f"Warehouse {warehouse} has {available_units} units of {product_id}.")

            elif choice == 2:
                # If choice is 2, display details about new product manufacturing
                st.write(f"Demand cannot be fully satisfied from warehouse inventory. {units - sum(supply_chain_data.values())} units will be made.")
                st.write(f"Total raw materials required: {supply_chain_data[0]}")  # Adjust based on your data format
                st.write(f"Cost to manufacture: {supply_chain_data[1]}")  # Adjust based on your data format
                st.write(f"Estimated time for manufacturing: {supply_chain_data[2]} hours")  # Adjust based on your data format

            elif choice == 3:
                # If choice is 3, show suppliers for the raw materials
                st.write(f"Demand cannot be satisfied as there are not enough parts to make new products.")
                st.write("Available Suppliers for the required raw materials:")
                for supplier in supply_chain_data:
                    st.write(supplier)  # Adjust based on your data structure

        
if __name__ == "__main__":
    main()
