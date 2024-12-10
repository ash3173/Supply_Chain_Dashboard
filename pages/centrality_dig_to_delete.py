import streamlit as st
import json
import pandas as pd

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

def display_node_boxes(first_row):
    st.write("## Key Schema Information")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(
            f"""
            **Business Group**
            {first_row['BusinessGroup']}
            """
        )
    with col2:
        st.info(
            f"""
            **Product Family**
            {first_row['ProductFamily']}
            """
        )
    with col3:
        st.info(
            f"""
            **Product Offering**
            {first_row['ProductOffering']}
            """
        )

    col4, col5, col6 = st.columns(3)
    with col4:
        st.info(
            f"""
            **Facility**
            {first_row['Facility']}
            """
        )
    with col5:
        st.info(
            f"""
            **Parts**
            {first_row['Parts']}
            """
        )
    with col6:
        st.info(
            f"""
            **Suppliers**
            {first_row['Suppliers']}
            """
        )

    col7 = st.columns(1)[0]
    with col7:
        st.info(
            f"""
            **Warehouse**
            {first_row['Warehouse']}
            """
        )
    
  
def main():
    st.title("Network Analysis Dashboard")
    
    # Process the data
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
    
    cols = st.columns(2)
    with cols[0]:
        st.subheader("Nodes with Highest Degree Centrality by Group")
        display_node_boxes(df)

if __name__ == "__main__":
   main()