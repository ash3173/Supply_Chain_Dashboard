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

def display_node_boxes(df):
    col1, col2, col3, col4 = st.columns(4)
    col5, col6, col7 = st.columns(3)
    
    # Get first row data
    first_row = df.iloc[0]
    
   
    box_style = """
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
            <div style="{box_style}">
                <h3>{first_row['BusinessGroup']}</h3>
                <p>Business Group</p>
            </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
            <div style="{box_style}">
                <h3>Product Family</h3>
                <p>{first_row['ProductFamily']}</p>
            </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
            <div style="{box_style}">
                <h3>Product Offering</h3>
                <p>{first_row['ProductOffering']}</p>
            </div>
        """, unsafe_allow_html=True)
        
    with col4:
        st.markdown(f"""
            <div style="{box_style}">
                <h3>Facility</h3>
                <p>{first_row['Facility']}</p>
            </div>
        """, unsafe_allow_html=True)
        
    with col5:
        st.markdown(f"""
            <div style="{box_style}">
                <h3>Parts</h3>
                <p>{first_row['Parts']}</p>
            </div>
        """, unsafe_allow_html=True)
        
    with col6:
        st.markdown(f"""
            <div style="{box_style}">
                <h3>Suppliers</h3>
                <p>{first_row['Suppliers']}</p>
            </div>
        """, unsafe_allow_html=True)
        
    with col7:
        st.markdown(f"""
            <div style="{box_style}">
                <h3>Warehouse</h3>
                <p>{first_row['Warehouse']}</p>
            </div>
        """, unsafe_allow_html=True)
  
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
    
    # Display results
    st.subheader("Network Analysis Results")
    st.write(f"Nodes with maximum connections ({max_connections} connections):", 
            ", ".join(max_connections_nodes))
    
    # Display boxes
    st.subheader("Nodes with Highest Degree Centrality by Group")
    display_node_boxes(df)

if __name__ == "__main__":
   main()