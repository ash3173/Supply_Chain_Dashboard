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
import math


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

# base_url = "http://172.17.149.238/api"
base_url = "https://viable-informally-alpaca.ngrok-free.app/api"
# version = "NSS_1000_12_Simulation" 
version = "lam_1000_12_v1"
# version = "simulation_exports_10000_50"
# version = "simulation_check"z

end_point_for_supplier = base_url

getVersions = f"{base_url}/versions"
getTimestamp = f"{base_url}/archive/schema/{version}"
getdata = f"{base_url}/archive/schema/{version}"

get_live_data = f"{base_url}/live/schema/{version}"

data_folder = "data"

# Streamlit app starts here
# main for running from server

def check_units_available_in_warehouse(data,graph,product_id,product_id_node) :

    in_edges = graph.in_edges(product_id_node[0],data=True)
    available = {}

    for source,target,edge_data in in_edges :
        if edge_data["relationship_type"] == "WAREHOUSEToPRODUCT_OFFERING" and target == product_id :
            if source not in available :
                available[source] = 0

            available[source] += edge_data["inventory_level"]

    all_warehouses = data["node_values"]["WAREHOUSE"]
    warehouses = {}

    # st.write(available)
    for warehouse_data in all_warehouses :
        # st.write(warehouse_data)
        if warehouse_data[-1] in available :
            name = warehouse_data[1]
            type = warehouse_data[2]
            location = warehouse_data[3]
            size_category = warehouse_data[4]
            warehouses[warehouse_data[-1]] = [name,type,location,size_category]

    # st.write(warehouses)
    return [available,warehouses]

def find_facilty_making_product(graph,product_id,product_id_node) :
    in_edges = graph.in_edges(product_id_node[0],data=True)
    facility = []

    for source,target,edge_data in in_edges :
        if edge_data["relationship_type"] == "FACILITYToPRODUCT_OFFERING" and target == product_id :
            facility.append(source)

    return facility

def find_raw_materials_to_make_product(data,facility) :
    raw_materials = {}
    facility_to_parts = data["link_values"]["PARTSToFACILITY"]
    for edge_data in facility_to_parts :
        # st.write(edge_data[-1],facility)
        if edge_data[-1] in facility :      # quantity , cost , lead time
            raw_materials[edge_data[-2]] = [edge_data[1],edge_data[3],edge_data[-3]] 

    return raw_materials

def find_total_cost(raw_materials,needed_units) :
    for key, values in raw_materials.items():
        raw_materials[key] = [math.ceil(value * needed_units) for value in values]
        # st.write("multipling",raw_materials[key],needed_units)

    return raw_materials

def calulate_cost_and_time(data,total,facility) :
    cost = 0
    time = 0
    for key, values in total.items():
        cost += values[1]
        time += values[2]

    all_facility = data["node_values"]["FACILITY"]

    for facility_data in all_facility :
        if facility_data[-1] in facility :
            cost += facility_data[-2]

    return cost,time

def check_warehouse_have_enough_raw_material(data,raw_materials) :
    warehouse = data["link_values"]["WAREHOUSEToPARTS"]
    all_raw_materials = {}
    for k,v in raw_materials.items() :
        all_raw_materials[k] = v[0]


    for edge_data in warehouse :
        if edge_data[-1] in all_raw_materials :
            all_raw_materials[edge_data[-1]] -= edge_data[1]

    for k,v in all_raw_materials.items() :
        if v > 0 :
            return [False,all_raw_materials]
    
    return [True,all_raw_materials]

# need to change
def get_supplier_for_raw_material(data,raw_materials) :
    path = "suppliers_parts_data_unused.json"
    with open(path,'r') as f : 
        supplier_data = json.load(f)
    
    
    # supplier_data = requests.get(end_point_for_supplier).json()

    parts_supplier = {}
    all_needed_supplier = set()
    for supp,parts in supplier_data.items() :
        
        for part in parts :
            if part in raw_materials :

                if part not in parts_supplier :
                    parts_supplier[part] = []

                parts_supplier[part].append(supp)
                all_needed_supplier.add(supp)

    all_suppliers = data["node_values"]["SUPPLIERS"]
    supplier_details = {}

    for supplier in all_suppliers :
        if supplier[-1] in all_needed_supplier : # location reliability size size_category
            supplier_details[supplier[-1]] = [supplier[2],supplier[3],supplier[4],supplier[5]]

    return [parts_supplier,supplier_details]



            
    # warehouses = data["link_values"]["WAREHOUSEToPARTS"]
    # warehouses_containing_raw_materials = []

    # for edge_data in warehouses :
    #     if edge_data[-1] in raw_materials :
    #         warehouses_containing_raw_materials.append(edge_data[-2])

    # suppliers = data["link_values"]["SUPPLIERSToWAREHOUSE"]
    # suppliers_for_raw_material = []

    # for edge_data in suppliers :
    #     if edge_data[-2] in warehouses_containing_raw_materials :
    #         suppliers_for_raw_material.append(edge_data[-1])

    return raw_materials



def supply_chain_query(data,graph,product_id,units,product_id_node) :

    warehouse_containing_product_id,warehouse_data = check_units_available_in_warehouse(data,graph,product_id,product_id_node)
    
    if sum(warehouse_containing_product_id.values()) >= units :
        return [1,[warehouse_containing_product_id,warehouse_data]] # 1 - Demand can be satisfied by warehouse
    
    else :

        # facility to parts - 
        # parts to facility - 
        # st.write(warehouse_containing_product_id)

        available_units = sum(warehouse_containing_product_id.values())
        facility = find_facilty_making_product(graph,product_id,product_id_node)
        # st.write("facility",facility)

        raw_materials = find_raw_materials_to_make_product(data,facility)
        # st.write("raw_materials",raw_materials)

        total_raw_materials = find_total_cost(raw_materials,units - available_units)

        check,needed_raw_material = check_warehouse_have_enough_raw_material(data,total_raw_materials)

        if check :
            cost,time = calulate_cost_and_time(data,total_raw_materials,facility)
            return [2,[total_raw_materials,cost,time,units - available_units]] # 2 - Demand can be satisfied by making new products
        
        else :
            supplier_data = get_supplier_for_raw_material(data,needed_raw_material)
            return [3,supplier_data] # 3 - Demand can't be satisfied as not enough parts to make new products


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

    if not os.path.exists(data_folder):
        os.makedirs(data_folder)

    target_path = os.path.join(data_folder, version)
    if os.path.exists(target_path) and os.path.isdir(target_path):
        
        st.info("Version exists!")
        st.write(getVersions)
        # all_files = [f for f in os.listdir(target_path) if os.path.isfile(os.path.join(target_path, f))]
        
        # # check if version exists in the server
        # all_versions = requests.get(getVersions).json()
        
        # if version not in all_versions:
        #     st.write("Version doesnt exist in the server")

        # else:
        #     st.write("Version exists in the server")

        #     all_timestamps = requests.get(getTimestamp).json()

        #     for timestamp in all_timestamps:
        #         if f"{timestamp}.json" not in all_files:
        #             timestamp_data = requests.get(f"{getdata}/{timestamp}").json()
        #             with open(os.path.join(target_path, f"{timestamp}.json"), "w") as f:
        #                 json.dump(timestamp_data, f, indent=4)

    else:
        st.info("Version doesnt exist, downloading...")
        os.makedirs(target_path)
        all_timestamps = requests.get(getTimestamp).json()

        for timestamp in all_timestamps:
            data = requests.get(f"{getdata}/{timestamp}")
            if data.status_code == 200 :
                timestamp_data = data.json()
                with open(os.path.join(target_path, f"{timestamp}.json"), "w") as f:
                    json.dump(timestamp_data, f, indent=4)
            else:
                st.write("Error in downloading the data")
                break

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

        st.markdown('<h2 class="custom-header">Graph Schema</h2>', unsafe_allow_html=True)


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
        units = st.number_input("Enter number of units",min_value=1,max_value=1000000)

        for node in graph.nodes(data=True):
            if node[0] == product_id :
                product_id_node = node
                break
        
        choice = 0
        if st.button("Check Supply Chain"):
            choice, supply_chain_data = supply_chain_query(data,graph, product_id, units, product_id_node)

    with col2:

        if choice != 0:
            # Handle the different cases returned by the query
            if choice == 1:
                # st.write(f"## Inventory and Demand Status")
                st.markdown(f"""
                    <div style="background-color: #f0f8ff; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
                        <h3 style="color: #2a9d8f; margin-bottom: 10px;">Demand Satisfied</h3>
                        <p style="font-size: 18px; color: #264653;">
                            ✅ <strong>Demand:</strong> {units} units can be satisfied.
                        </p>
                        <p style="font-size: 18px; color: #264653;">
                            📦 <strong>Total Available Units of {product_id}:</strong> {math.ceil(sum(supply_chain_data[0].values()))}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
 
                st.write("### Warehouse Details")
                st.write(f"Below is the breakdown of available units for **{product_id}** across warehouses:")

                # Preparing data for table display
                warehouse_data = []
                for warehouse, prop in supply_chain_data[1].items():
                    warehouse_data.append({
                        "Warehouse": warehouse,
                        "Units Available": math.ceil(supply_chain_data[0][warehouse]),
                        "Name": prop[0],
                        "Type": prop[1],
                        "Location": prop[2],
                        "Size": prop[3]
                    })

                # Convert to DataFrame
                warehouse_df = pd.DataFrame(warehouse_data)

                # Display the table
                st.dataframe(warehouse_df)

            elif choice == 2:

                # If choice is 2, display details about new product manufacturing
                # st.write(f"Demand cannot be fully satisfied from warehouse inventory. {math.ceil(supply_chain_data[-1])} units will be made.")
                # st.write(f"Total raw materials required to make {math.ceil(supply_chain_data[-1])} units: {supply_chain_data[0]}")  # Adjust based on your data format
                # st.write(f"Total Cost required to manufacture : {supply_chain_data[1]}")  # Adjust based on your data format
                # st.write(f"Estimated time for manufacturing: {supply_chain_data[2]} hours")  # Adjust based on your data format

                units_to_be_made = math.ceil(supply_chain_data[-1])
                raw_materials = supply_chain_data[0]
                total_cost = supply_chain_data[1]
                estimated_time = supply_chain_data[2]

                # Displaying information in a structured format
                # st.write(f"### Manufacturing Summary")
                # st.write(f"**Demand cannot be fully satisfied from warehouse inventory.**")
                # st.write(f"- **Units to be manufactured:** {units_to_be_made}")
                # st.write("")
                st.markdown(f"""
                    <div style="background-color: #f7faff; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                        <h2 style="color: #0073e6; margin: 0;">Manufacturing Summary</h2>
                        <p style="font-size: 18px; color: #333; margin: 5px 0;">
                            <strong>Demand cannot be fully satisfied from warehouse inventory.</strong>
                        </p>
                        <ul style="font-size: 16px; color: #555; margin: 10px 0;">
                            <li><strong>Units to be Manufactured:</strong> {units_to_be_made}</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)


                st.write(f"### Raw Materials Breakdown")
                st.write(f"To manufacture **{units_to_be_made} units**, the following raw materials are required:")
                # for material, values in raw_materials.items():
                #     st.write(f"- **{material}**: Quantity: {values[0]}, Cost: {values[1]}, Time: {values[2]} hours")
                # st.write("")

                raw_materials_df = pd.DataFrame.from_dict(
                    raw_materials, 
                    orient="index", 
                    columns=["Quantity", "Cost", "Time (hours)"]
                ).reset_index().rename(columns={"index": "Material"})

                # Display the table
                st.dataframe(raw_materials_df)


                # st.write(f"### Manufacturing Cost and Time")
                # Highlighting cost and time using HTML and Markdown
                st.markdown(f"""
                <div style="background-color: #f0f8ff; padding: 10px; border-radius: 5px;">
                    <h3 style="color: #ff4500; margin: 0;"> 💰 Total Cost to Manufacture: ${total_cost:,.2f}</h3>
                    <p style="font-size: 18px; color: #4682b4; margin: 0;"> ⏳ Estimated Manufacturing Time:  {estimated_time} hours</p>
                </div>
                """, unsafe_allow_html=True)


                # st.write(f"- **Total Cost to Manufacture:** ${total_cost:,.2f}")
                # st.write(f"- **Estimated Manufacturing Time:** {estimated_time} hours")


            elif choice == 3:
                st.markdown(f"""
                    <div style="background-color: #ffe6e6; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                        <h2 style="color: #d9534f; margin: 0;">Demand Cannot Be Satisfied</h2>
                        <p style="font-size: 18px; color: #333; margin: 5px 0;">
                            There are not enough parts to manufacture new products.
                        </p>
                    </div>

                    """, unsafe_allow_html=True)
                    # <div style="background-color: #f9f9f9; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                    #     <h3 style="color: #5bc0de; margin: 0;">Available Suppliers for the Required Raw Materials:</h3>
                    # </div>

                st.write("### Available Suppliers for the Required Raw Materials")
                
                parts_data = supply_chain_data[0]  # Part and supplier mapping
                supplier_data = supply_chain_data[1]  # Supplier details

                # Process and display suppliers for each part
                for part, suppliers in parts_data.items():
                    part_table_data = []

                    for supplier in suppliers:
                        if supplier in supplier_data:  # Check if supplier data is available
                            supplier_details = supplier_data[supplier]
                            part_table_data.append({
                                "Supplier": supplier,
                                "Location": supplier_details[0],
                                "Reliability (%)": f"{supplier_details[1] * 100:.2f}",
                                "Capacity": supplier_details[2],
                                "Size": supplier_details[3].capitalize()  # Capitalize size for consistent display
                            })

                    # Display supplier table if data exists
                    if part_table_data:
                        st.write(f"### Part: {part}")
                        st.write(f"Available suppliers for **{part}** are listed below:")
                        part_df = pd.DataFrame(part_table_data)
                        st.dataframe(part_df)

                # Show a message if no data is available
                if not any(supplier in supplier_data for suppliers in parts_data.values() for supplier in suppliers):
                    st.write("No supplier data is available for the required raw materials.")

                # for supplier in supply_chain_data:
                #     st.write(supplier)  # Adjust based on your data structure


        
if __name__ == "__main__":
    main()
