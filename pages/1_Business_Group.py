import streamlit as st
import requests
from constants import getTimestamp, getdata
import heapq
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
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
    cols0,cols2=st.columns([3,1],gap='large')
    with cols0:
        timerange = st.slider("Select a range of timestamp", 0, len(st.session_state.temporal_graph.files), (0,len(st.session_state.temporal_graph.files)))
        start_range, end_range = timerange

    # with cols2:
    #     st.write(" ")
    #     st.write(" ")
    #     st.write(" ")
    #     timerange = st.slider("Select a range of timestamp", 0, len(st.session_state.temporal_graph.files), (0,len(st.session_state.temporal_graph.files)))
    
    # Validate session state
    

    highest_business_group = []  # Heap to store the highest business groups
    revenue_of_business_group_across_time = {}
    # totalTimeStamps = len(st.session_state.temporal_graph.files)
    
    for time in range(start_range, end_range):
        data = st.session_state.temporal_graph.load_json_at_timestamp(time)
        business_nodes = data["node_values"]["BUSINESS_GROUP"]
        # st.write(business_nodes[0])
        
        for i in range(len(business_nodes)):
            heapq.heappush(highest_business_group, (business_nodes[i][-2], business_nodes[i][-1], time))
            if len(highest_business_group) > 3:
                heapq.heappop(highest_business_group)

            if business_nodes[i][-1] not in revenue_of_business_group_across_time :
                revenue_of_business_group_across_time[business_nodes[i][-1]] = []

            revenue_of_business_group_across_time[business_nodes[i][-1]].append((time,business_nodes[i][-2]))
    
    # Display the top 3 business groups in columns
    cols = st.columns(len(highest_business_group)+1)
    with cols[0]:
        fig = create_graph()
        st.plotly_chart(fig, use_container_width=True)
    
    highest_business_group.sort(reverse=True)
    for i in range(len(highest_business_group)):
        revenue, identifier, month_index = highest_business_group[i]
        fig2 = plot_higest_revenue(revenue, identifier, month_index)
        with cols[i+1]:
            st.pyplot(fig2)
    
    st.markdown("<hr style='margin-top: -50px; margin-bottom: -50px; border: none; border-top: 1px solid #ccc;' />", unsafe_allow_html=True)
    fig1 = plot_revenue(revenue_of_business_group_across_time)
    st.plotly_chart(fig1, use_container_width=True)

@st.fragment
def node_details_input():
    
    col1, col2 = st.columns([1.5, 1],gap="large")
    with col2:
        st.write("###")
        timestamp = st.slider("Select Timestamp", min_value=0, max_value=len(st.session_state.temporal_graph.files)-1)
    with col1:
        
        bg_index = st.session_state.temporal_graph.create_node_type_index(timestamp)["BUSINESS_GROUP"]
        st.write("### Business Group Information Viewer")
        
        # Use the keys of the index dictionary directly
        all_business_groups = ["Select Business Group"] + list(bg_index.keys())

        business_group_id = st.selectbox("Choose Business Id", all_business_groups)
    if business_group_id != "Select Business Group":
        # node_details(node_index, business_group_id)
        node_details(bg_index, business_group_id,timestamp)
    


    
@st.fragment
@time_and_memory_streamlit
def node_details(node_index, business_group_id,timestamp):
    col1, col2 = st.columns(2)
    with col1:
        st.write("### Business Group Info")
        
        # Fetch details directly from the index dictionary
        node_data = node_index.get(business_group_id)
        
        if node_data:
            attributes = [
                ("Node Type", "🔗"),
                ("Name", "📛"),
                ("Description", "📝"),
                ("Revenue", "💰"),
                ("ID", "🆔")
            ]
            st.markdown("""
            <style>
                .business-group-table {
                    width: 100%;
                    margin-top: 20px;
                    border-collapse: collapse;
                    font-size: 16px;
                    font-family: Arial, sans-serif;
                }
                .business-group-table td {
                    padding: 8px 12px;
                }
                .business-group-table td:first-child {
                    font-weight: bold;
                    color: #0d47a1; /* Blue color for attribute labels */
                    width: 40%;
                    text-align: left;
                }
                .business-group-table td:last-child {
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
                <table class="business-group-table">
                    {table_rows}
                </table>
                """,
                unsafe_allow_html=True
            )
        else:
            st.warning("Business Group ID not found.")


    with col2:
        # if found:
        graph=st.session_state.temporal_graph.load_graph_at_timestamp(timestamp)
        ego_graph = ego_graph_query(graph, business_group_id, 1)
        if ego_graph:
            st.write(f"### Neighbors for {business_group_id}")
            # st.write(f"Ego Graph for Node: {supplier_id}")
            # st.write(f"Nodes: {ego_graph.number_of_nodes()}, Edges: {ego_graph.number_of_edges()}")

            # Visualize and render the ego graph with Plotly
            fig = plotly_ego_graph(ego_graph)
            st.plotly_chart(fig)  # Display the figure in Streamlit


def create_graph():
    nodes = {
        'Business Group': ['node_type', 'name', 'description', 'revenue', 'id'],
        'Product Family': ['node_type', 'name', 'revenue', 'id']
    }
    edge = ['relationship_type','source', 'target']  # Attributes for the edge

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=[0, 0.6], y=[0, -0.3], mode='lines', line=dict(width=2, color='white'),
        hoverinfo='text',
        text=['<b>Edge Attributes</b><br>' + '<br>'.join(edge)]  # Edge hover text
    ))

    fig.add_trace(go.Scatter(
        x=[0], y=[0], mode='markers+text', marker=dict(size=15, color='cyan'),
        text=['Business Group'], textposition='top center', hoverinfo='text',
        hovertext='<b>Business Group</b><br>' + '<br>'.join(nodes['Business Group'])  # Attributes for hover
    ))

    fig.add_trace(go.Scatter(
        x=[0.6], y=[-0.3], mode='markers+text', marker=dict(size=15, color='orange'),
        text=['Product Family'], textposition='top center', hoverinfo='text',
        hovertext='<b>Product Family</b><br>' + '<br>'.join(nodes['Product Family'])  # Attributes for hover
    ))

    fig.update_layout(
        title=dict(
            text="Business Group Schema",  # Title text
            x=0.5,  # Center the title
            xanchor='center',  # Horizontal alignment
            yanchor='top'  # Vertical alignment
        ),
        height=250, 
        margin=dict(l=10, r=10, t=30, b=10),  # Tighten the margins
        xaxis=dict(
            showgrid=False, zeroline=False, showticklabels=False,
            range=[-0.2, 0.8]  # Adjust x-axis range for padding
        ),
        yaxis=dict(
            showgrid=False, zeroline=False, showticklabels=False,
            range=[-0.4, 0.2]  # Adjust y-axis range for padding
        ),
        showlegend=False,
        font=dict(color="white", size=10),  # Reduce font size for text
        hoverlabel=dict(bgcolor="black", font_color="white"),  # Hover label styling
        plot_bgcolor='rgba(0,0,0,0)',  # Transparent background
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent paper background
    )

    return fig

def plot_revenue(data):
    # Extract business group IDs and their respective data
    business_units = list(data.keys())
    num_business_units = len(business_units)

    fig = make_subplots(
        rows=1, cols=num_business_units,
        subplot_titles=[f"{unit}" for unit in business_units]
    )

    # Colors for each business unit
    colors = ['#2196F3', '#4CAF50', '#FF9800', '#9C27B0', '#FFC107', '#00BCD4', '#795548', '#607D8B']

    # Plot each business unit
    for i, unit in enumerate(business_units):
        unit_data = data[unit]
        x_values = [item[0] for item in unit_data]  # Extract timestamps
        y_values = [item[1] for item in unit_data]  # Extract revenues

        # Add the line plot with shaded area
        fig.add_trace(
            go.Scatter(
                x=x_values,
                y=y_values,
                mode='lines',
                line=dict(color=colors[i % len(colors)], width=2),
                fill='tozeroy',  # Fill area under the line
                fillcolor=f"rgba({int(colors[i % len(colors)][1:3], 16)}, "
                          f"{int(colors[i % len(colors)][3:5], 16)}, "
                          f"{int(colors[i % len(colors)][5:], 16)}, 0.3)",
                name=f"{unit}"
            ),
            row=1, col=i+1
        )

    # Consistent y-axis limits
    max_y = max([max([item[1] for item in data[unit]]) for unit in business_units]) * 1.1
    for i in range(1, num_business_units + 1):
        fig.update_yaxes(range=[0, max_y], title="Revenue", row=1, col=i)
        fig.update_xaxes(title="Time", row=1, col=i)

    fig.update_layout(
        title="Revenue Generated by Business Units Over Time",
        height=500,  
        width=600 * num_business_units,  
        template="plotly_dark" 
    )

    return fig
    
def plot_higest_revenue(revenue, identifier, m):
    fig, ax = plt.subplots(figsize=(3, 3), facecolor='none')  
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    
    # Draw a circle in the middle
    circle = Circle((0, 0.5), 0.4, edgecolor='#2596be', facecolor='none', linewidth=6)
    ax.add_artist(circle)
    
    # Add identifier text
    ax.text(
        0, 0.5, identifier, 
        fontsize=12, ha='center', va='center', color='#2596be', style='italic', weight='bold'
    )
    
    # Add revenue text
    ax.text(
        0, -0.2, f"Revenue: {revenue}", 
        fontsize=10, ha='center', va='center', color='white', style='italic', weight='bold'
    )

    # Add month text
    ax.text(
        0, -0.4, f"Month: {m}", 
        fontsize=10, ha='center', va='center', color='white', style='italic', weight='bold'
    )    
    
    ax.axis('off')

    fig.patch.set_alpha(0)
    
    plt.tight_layout(pad=0.1)  # Minimized padding

    return fig


def main():
    # Adjust global Streamlit styling
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
    st.title("Business Group Dashboard")
    if "temporal_graph" not in st.session_state:
        st.error("No Temporal Graph found in the session state. Please run the main script first.")
        return
    static_part()


    st.divider()  
    node_details_input()


    st.text(" ")  
    st.text(" ") 

    st.divider()  
    
if __name__ == "__main__":
    main()