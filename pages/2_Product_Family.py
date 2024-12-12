import streamlit as st
import requests
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import networkx as nx

from utils import time_and_memory_streamlit, plotly_ego_graph, ego_graph_query

# st.set_page_config(
#     layout="wide",
#     initial_sidebar_state="expanded",
#     )

@st.fragment
def static_part():
    totalTimeStamps=len(st.session_state.temporal_graph.files)
    highest_quarterly_revenue = [0, 0, 0, 0]
    percent_revenue = [0, 0, 0, 0]
    highest_quarterly_revenue_product_group = ["", "", "", ""]
    q1,q2={},{}
    q3,q4={},{}
    revenue_of_product_offering_across_time = {}
    pf_data={"PF_001":"Kyo","PF_002":"Coronus","PF_003":"Flex","PF_004":"Versys Metal"}
    
    for time in range(totalTimeStamps) :
        
        data = st.session_state.temporal_graph.load_json_at_timestamp(time)
        

        PRODUCT_FAMILY = data["node_values"]["PRODUCT_FAMILY"]

        for i in range(len(PRODUCT_FAMILY)) :
            if PRODUCT_FAMILY[i][1] not in revenue_of_product_offering_across_time :
                revenue_of_product_offering_across_time[PRODUCT_FAMILY[i][1]] = []

            revenue_of_product_offering_across_time[PRODUCT_FAMILY[i][1]].append(PRODUCT_FAMILY[i][-2])

        product_index=st.session_state.temporal_graph.create_node_type_index(time)["PRODUCT_FAMILY"]
        
        for key,value in product_index.items():
            if time % 12 in [0,1,2]:
                if pf_data[key] not in q1:
                    q1[pf_data[key]] = 0
                q1[pf_data[key]]+=value[-2]

            elif time % 12 in [3,4,5]:
                if pf_data[key] not in q2:
                    q2[pf_data[key]] = 0
                q2[pf_data[key]]+=value[-2]
            
            elif time % 12 in [6,7,8]:
                if pf_data[key] not in q3:
                    q3[pf_data[key]] = 0
                q3[pf_data[key]]+=value[-2]
            
            else:
                if pf_data[key] not in q4:
                    q4[pf_data[key]] = 0
                q4[pf_data[key]]+=value[-2]
    
    highest_quarterly_revenue_product_group[0]=max(q1, key=lambda x:q1[x])
    highest_quarterly_revenue[0] = round(q1[highest_quarterly_revenue_product_group[0]], 3)
    percent_revenue[0]=round((highest_quarterly_revenue[0]/sum(q1.values()))*100,3)
    

    highest_quarterly_revenue_product_group[1]=max(q2, key=lambda x:q2[x])
    highest_quarterly_revenue[1] = round(q2[highest_quarterly_revenue_product_group[0]], 3)
    percent_revenue[1]=round((highest_quarterly_revenue[1]/sum(q2.values()))*100,3)
    
    highest_quarterly_revenue_product_group[2]=max(q3, key=lambda x:q3[x])
    highest_quarterly_revenue[2] = round(q3[highest_quarterly_revenue_product_group[0]], 3)
    percent_revenue[2]=round((highest_quarterly_revenue[2]/sum(q3.values()))*100,3)

    highest_quarterly_revenue_product_group[3]=max(q4, key=lambda x:q4[x])
    highest_quarterly_revenue[3] = round(q4[highest_quarterly_revenue_product_group[0]], 3)
    percent_revenue[3]=round((highest_quarterly_revenue[3]/sum(q4.values()))*100,3)
    
    

    cols = st.columns(4)

    for i in range(4) :
        revenue, identifier = highest_quarterly_revenue[i], highest_quarterly_revenue_product_group[i]
        fig = plot_higest_revenue(revenue, identifier, i+1,percent_revenue[i])
        with cols[i]:
            st.pyplot(fig)
    cols=st.columns([1,3])
    with cols[0]:
        fig = create_graph()
        st.plotly_chart(fig, use_container_width=True)
    with cols[1]:
        fig1,fig2 = plot_revenues(revenue_of_product_offering_across_time)
        st.plotly_chart(fig1, use_container_width=True)
    st.plotly_chart(fig2, use_container_width=True)
def create_graph():
    # Define node attributes
    nodes = {
        "BUSINESS_GROUP": ["node_type", "name", "description", "revenue", "id"],
        "PRODUCT_FAMILY": ["node_type", "name", "revenue", "id"],
        "PRODUCT_OFFERING": ["node_type", "name", "cost", "demand", "id"]
    }

    # Define edge attributes
    edges = {
        "BUSINESS_GROUPToPRODUCT_FAMILY": ["relationship_type", "source", "target"],
        "PRODUCT_FAMILYToPRODUCT_OFFERING": ["relationship_type", "source", "target"]
    }

    # Create a new figure
    fig = go.Figure()

    # Add edge: BUSINESS_GROUP to PRODUCT_FAMILY
    fig.add_trace(go.Scatter(
        x=[0, 0.5], y=[0, -0.3], mode='lines', line=dict(width=2, color='white'),
        hoverinfo='text',
        text=['<b>BUSINESS_GROUPToPRODUCT_FAMILY</b><br>' + '<br>'.join(edges["BUSINESS_GROUPToPRODUCT_FAMILY"])]
    ))

    # Add edge: PRODUCT_FAMILY to PRODUCT_OFFERING
    fig.add_trace(go.Scatter(
        x=[0.5, 1], y=[-0.3, -0.6], mode='lines', line=dict(width=2, color='white'),
        hoverinfo='text',
        text=['<b>PRODUCT_FAMILYToPRODUCT_OFFERING</b><br>' + '<br>'.join(edges["PRODUCT_FAMILYToPRODUCT_OFFERING"])]
    ))

    # Add BUSINESS_GROUP node
    fig.add_trace(go.Scatter(
        x=[0], y=[0], mode='markers+text', marker=dict(size=15, color='cyan'),
        text=['BUSINESS_GROUP'], textposition='top center', hoverinfo='text',
        hovertext='<b>BUSINESS_GROUP</b><br>' + '<br>'.join(nodes["BUSINESS_GROUP"])
    ))

    # Add PRODUCT_FAMILY node
    fig.add_trace(go.Scatter(
        x=[0.5], y=[-0.3], mode='markers+text', marker=dict(size=15, color='orange'),
        text=['PRODUCT_FAMILY'], textposition='top center', hoverinfo='text',
        hovertext='<b>PRODUCT_FAMILY</b><br>' + '<br>'.join(nodes["PRODUCT_FAMILY"])
    ))

    # Add PRODUCT_OFFERING node
    fig.add_trace(go.Scatter(
        x=[1], y=[-0.6], mode='markers+text', marker=dict(size=15, color='green'),
        text=['PRODUCT_OFFERING'], textposition='top center', hoverinfo='text',
        hovertext='<b>PRODUCT_OFFERING</b><br>' + '<br>'.join(nodes["PRODUCT_OFFERING"])
    ))

    # Update layout for visibility
    fig.update_layout(
        title=dict(
            text="Product Family Schema",
            x=0, xanchor='left', yanchor='top'
        ),
        height=400,
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


def plot_revenues(data):
    
    # Colors for the plots (cyclic if there are more units than colors)
    colors = [
        '#2196F3', '#4CAF50', '#FF9800', '#9C27B0', '#FFC107', '#00BCD4', '#795548', '#607D8B'
    ]

    num_business_units = len(data)

    # Create subplot layout
    fig2 = make_subplots(
        rows=1,
        cols=num_business_units,
        subplot_titles=list(data.keys())  # Titles for each subplot
    )

    # Create a combined figure (fig1)
    fig1 = go.Figure()

    # Generate plots for each business unit
    for i, (business_unit, revenues) in enumerate(data.items()):
        # Set fillcolor in rgba format (adjust transparency to 0.2)
        fillcolor = f"rgba({int(colors[i % len(colors)][1:3], 16)}, {int(colors[i % len(colors)][3:5], 16)}, {int(colors[i % len(colors)][5:7], 16)}, 0.2)"

        # Add to Subplot (fig2)
        fig2.add_trace(
            go.Scatter(
                x=list(range(len(revenues))),
                y=revenues,
                mode='lines',
                fill='tozeroy',
                name=business_unit,
                line=dict(color=colors[i % len(colors)], width=2),
                fillcolor=fillcolor
            ),
            row=1,
            col=i + 1
        )

        # Add to Combined Figure (fig1)
        fig1.add_trace(go.Scatter(
            x=list(range(len(revenues))),
            y=revenues,
            mode='lines',
            fill='tozeroy',
            name=business_unit,
            line=dict(color=colors[i % len(colors)], width=2),
            fillcolor=fillcolor
        ))

    # Customize the layout for fig2 (subplots)
    fig2.update_layout(
        title='Revenue Generated by Product Family Over Time',
        title_x=0,
        height=250,  # Fixed height
        width=500 * num_business_units,  # Adjust width dynamically
        template='plotly_dark',
        showlegend=False,
        margin=dict(t=50, b=30, l=30, r=30)
    )
    fig2.update_annotations(font_size=12)

    # Customize the layout for combined_fig (fig1)
    fig1.update_layout(
        title="Combined Revenue Figures",
        title_x=0,
        xaxis_title="Time",
        yaxis_title="Revenue",
        template='plotly_dark',
        hovermode='x unified',
        margin=dict(l=50, r=50, t=50, b=50)
    )

    return fig1, fig2

@st.fragment
def node_details_input():

    col1, col2 = st.columns([1.5, 1],gap="large")
    with col2:
        st.write("###")
        timestamp = st.slider("Select Timestamp", min_value=0, max_value=len(st.session_state.temporal_graph.files) - 1)
    with col1:
        
        pf_index = st.session_state.temporal_graph.create_node_type_index(timestamp)["PRODUCT_FAMILY"]
        # Heading for the Business Group Info
        st.write("### Product Family Information Viewer")
        
        # Use the keys of the index dictionary directly
        all_pf = ["Select Product Family"] + list(pf_index.keys())

        # Create a selectbox using these keys
        pf_id_input = st.selectbox("Choose Product Family Id",all_pf)
    # Display node details if a valid business group is selected
    if pf_id_input!="Select Product Family":
        node_details(pf_index, pf_id_input,timestamp)

@st.fragment
@time_and_memory_streamlit
def node_details(node_index, product_family_id,timestamp):
    col1, col2 = st.columns(2)
    with col1:
        st.write("### Product Family Info")
        
        # Fetch details directly from the index dictionary
        node_data = node_index.get(product_family_id)
        
        if node_data:
            attributes = [
            ("Node Type", "🔗"),
            ("Name", "📛"),
            ("Revenue", "💰"),
            ("ID", "🆔")
            ]
            # Style for the no-border table
            st.markdown("""
            <style>
                .product-family-table {
                    width: 100%;
                    margin-top: 20px;
                    border-collapse: collapse;
                    font-size: 16px;
                    font-family: Arial, sans-serif;
                }
                .product-family-table td {
                    padding: 8px 12px;
                }
                .product-family-table td:first-child {
                    font-weight: bold;
                    color: #0d47a1; /* Blue color for attribute labels */
                    width: 40%;
                    text-align: left;
                }
                .product-family-table td:last-child {
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
                    <table class="product-family-table">
                        {table_rows}
                    </table>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.warning('Enter a valid Product Family ID')

    with col2:
        # if found:
        graph=st.session_state.temporal_graph.load_graph_at_timestamp(timestamp)
        ego_graph = ego_graph_query(graph, product_family_id, 1)
        if ego_graph:
            st.write(f"### Neighbors for {product_family_id}")
            # st.write(f"Ego Graph for Node: {supplier_id}")
            # st.write(f"Nodes: {ego_graph.number_of_nodes()}, Edges: {ego_graph.number_of_edges()}")

            # Visualize and render the ego graph with Plotly
            fig = plotly_ego_graph(ego_graph)
            st.plotly_chart(fig)  # Display the figure in Streamlit


# @st.fragment
# def node_details(PRODUCT_FAMILY):
#     col1, col2=st.columns(2)

#     with col1:
#         # Heading for the Product Family Info
#         st.write("### Product Family Info")

#         # Input field for Product Family ID
#         product_family_id = st.text_input("Enter Product Family ID (e.g., PF_001):", placeholder="Search for Product Family ID...")

#         # Define the attributes of the product family
#         attributes = [
#             ("Node Type", "🔗"),
#             ("Name", "📛"),
#             ("Revenue", "💰"),
#             ("ID", "🆔")
#         ]

#         # Style for the no-border table
#         st.markdown("""
#             <style>
#                 .product-family-table {
#                     width: 100%;
#                     margin-top: 20px;
#                     border-collapse: collapse;
#                     font-size: 16px;
#                     font-family: Arial, sans-serif;
#                 }
#                 .product-family-table td {
#                     padding: 8px 12px;
#                 }
#                 .product-family-table td:first-child {
#                     font-weight: bold;
#                     color: #0d47a1; /* Blue color for attribute labels */
#                     width: 40%;
#                     text-align: left;
#                 }
#                 .product-family-table td:last-child {
#                     color: #2596be; /* Gray color for attribute values */
#                     width: 60%;
#                     text-align: left;
#                 }
#             </style>
#         """, unsafe_allow_html=True)

#         found = False

#         # Loop through product family data to find matching Product Family ID and display details
#         for val in PRODUCT_FAMILY:  # Replace with your actual product family data source
#             if product_family_id and product_family_id in val:
#                 found = True

#                 # Create a no-border table for displaying attributes and values
#                 table_rows = ""
#                 for attr, icon in attributes:
#                     # Extract values dynamically based on attributes
#                     table_rows += f"<tr><td>{icon} {attr}:</td><td>{val[attributes.index((attr, icon))]}</td></tr>"

#                 # Display the table
#                 st.markdown(
#                     f"""
#                     <table class="product-family-table">
#                         {table_rows}
#                     </table>
#                     """,
#                     unsafe_allow_html=True
#                 )

#         if not found:
#             st.warning('Enter a valid Product Family ID')

#     with col2:
#         if found:
#             graph=st.session_state.temporal_graph.load_graph_at_timestamp(1)
#             ego_graph = ego_graph_query(graph, product_family_id, 1)
#             if ego_graph:
#                 st.write(f"### Neighbors for {product_family_id}")
#                 # st.write(f"Ego Graph for Node: {supplier_id}")
#                 # st.write(f"Nodes: {ego_graph.number_of_nodes()}, Edges: {ego_graph.number_of_edges()}")

#                 # Visualize and render the ego graph with Plotly
#                 fig = plotly_ego_graph(ego_graph)
#                 st.plotly_chart(fig)  # Display the figure in Streamlit



def plot_higest_revenue(revenue, identifier,q,percent_revenue):

    fig, ax = plt.subplots(figsize=(4, 4), facecolor='none')
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    
    circle = Circle((0, 0.5), 0.4, edgecolor='#2596be', facecolor='none', linewidth=6)
    ax.add_artist(circle)
    
    ax.text(
        0, 0.5, identifier, 
        fontsize=16, ha='center', va='center', color='#2596be', style='italic', weight='bold'
    )
    
    ax.text(
        0, -0.2, f"Revenue : {revenue}", 
        fontsize=12, ha='center', va='center', color='white', style='italic', weight='bold'
    )

    ax.text(
        0, -0.4, f"Percentage Revenue : {percent_revenue}%", 
        fontsize=12, ha='center', va='center', color='white', style='italic', weight='bold'
    )

    ax.text(
        0, -0.6, f"Fiscal Quarter : {q}", 
        fontsize=12, ha='center', va='center', color='white', style='italic', weight='bold'
    )    
    
    ax.axis('off')
    fig.patch.set_alpha(0)

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

    st.title("Product Family Dashboard")
    if "temporal_graph" not in st.session_state:
        st.error("No Temporal Graph found in the session state. Please run the main script first.")
        return
    
    static_part()

    st.divider()  
    node_details_input()
    st.text(" ")  # Adds one blank line
    st.text(" ")  # Adds another blank line

    st.divider()  # Adds a horizontal divider (thin line), visually separating sections
if __name__ == "__main__":
    main()