import streamlit as st
import requests
from constants import getTimestamp, getdata
import heapq
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import networkx as nx
import time
import tracemalloc
import functools

st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
    )

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



# @st.fragment
# def node_details_input(timestamp):
#     col1, col2 = st.columns([2, 1])
#     with col1:
        
#         bg_index = st.session_state.temporal_graph.create_node_type_index(timestamp)["BUSINESS_GROUP"]
#         # Heading for the Business Group Info
#         st.write("### Business Group Info")
        
#         # Use the keys of the index dictionary directly
#         all_business_groups = ["Select Business Group"] + list(bg_index.keys())

#         # Create a selectbox using these keys
#         business_group_id = st.selectbox("Choose Business Id", all_business_groups)
#     # Display node details if a valid business group is selected
#     if business_group_id != "Select Business Group":
#         # node_details(node_index, business_group_id)
#         node_details(bg_index, business_group_id)


@st.fragment
def node_details_input(business_nodes):
    col1,col2=st.columns([2,1])
    with col1:
        # Heading for the Business Group Info
        st.write("### Business Group Info")
        all_business_groups = ["Select Business Group"]
        for business_group in business_nodes:
            all_business_groups.append(business_group[-1])


        business_group_id = st.selectbox("Choose Business Id",all_business_groups)
    
    if business_group_id!="Select Business Group":
        node_details(business_nodes, business_group_id)

@st.fragment
@time_and_memory_streamlit
def node_details(business_nodes,business_group_id):
    col1, col2=st.columns(2)
    with col1:
        # Heading for the Business Group Info
        st.write("### Business Group Info")
    
        attributes = [
            ("Node Type", "🔗"),
            ("Name", "📛"),
            ("Description", "📝"),
            ("Revenue", "💰"),
            ("ID", "🆔")
        ]

        # Style for the no-border table
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

        found = False

        # Loop through business group data to find matching Business Group ID and display details
        for val in business_nodes:  # Replace with your actual business group data source
            if business_group_id and business_group_id in val:
                found = True

                # Create a no-border table for displaying attributes and values
                table_rows = ""
                for attr, icon in attributes:
                    # Extract values dynamically based on attributes
                    table_rows += f"<tr><td>{icon} {attr}:</td><td>{val[attributes.index((attr, icon))]}</td></tr>"

                # Display the table
                st.markdown(
                    f"""
                    <table class="business-group-table">
                        {table_rows}
                    </table>
                    """,
                    unsafe_allow_html=True
                )

        if not found:
            st.warning('Enter a valid Business Group ID')
        with col2:
            if found:
                graph=st.session_state.temporal_graph.load_graph_at_timestamp(2)
                ego_graph = ego_graph_query(graph, business_group_id, 1)
                if ego_graph:
                    st.write(f"### Neighbors for {business_group_id}")
                    # st.write(f"Ego Graph for Node: {supplier_id}")
                    # st.write(f"Nodes: {ego_graph.number_of_nodes()}, Edges: {ego_graph.number_of_edges()}")

                    # Visualize and render the ego graph with Plotly
                    fig = plotly_ego_graph(ego_graph)
                    st.plotly_chart(fig)  # Display the figure in Streamlit
# @st.fragment
# @time_and_memory_streamlit
# def node_details(node_index, business_group_id):
#     col1, col2 = st.columns(2)
#     with col1:
#         st.write("### Business Group Info")
        
#         # Fetch details directly from the index dictionary
#         node_data = node_index.get(business_group_id)
        
#         if node_data:
#             attributes = [
#                 ("Node Type", "🔗"),
#                 ("Name", "📛"),
#                 ("Description", "📝"),
#                 ("Revenue", "💰"),
#                 ("ID", "🆔")
#             ]

#             # Ensure node_data is a list and extract values based on their order
#             table_rows = ""
#             for index, (attr, icon) in enumerate(attributes):
#                 value = node_data[index] if index < len(node_data) else "N/A"
#                 table_rows += f"<tr><td>{icon} {attr}:</td><td>{value}</td></tr>"

#             st.markdown(
#                 f"""
#                 <table class="business-group-table">
#                     {table_rows}
#                 </table>
#                 """,
#                 unsafe_allow_html=True
#             )
#         else:
#             st.warning("Business Group ID not found.")


#     with col2:
#         # if found:
#         graph=st.session_state.temporal_graph.load_graph_at_timestamp(2)
#         ego_graph = ego_graph_query(graph, business_group_id, 1)
#         if ego_graph:
#             st.write(f"### Neighbors for {business_group_id}")
#             # st.write(f"Ego Graph for Node: {supplier_id}")
#             # st.write(f"Nodes: {ego_graph.number_of_nodes()}, Edges: {ego_graph.number_of_edges()}")

#             # Visualize and render the ego graph with Plotly
#             fig = plotly_ego_graph(ego_graph)
#             st.plotly_chart(fig)  # Display the figure in Streamlit
def create_graph():
    # Define node attributes for Business Group and Product Family
    nodes = {
        'Business Group': ['node_type', 'name', 'description', 'revenue', 'id'],
        'Product Family': ['node_type', 'name', 'revenue', 'id']
    }
    edge = ['relationship_type','source', 'target']  # Attributes for the edge

    # Create a new figure
    fig = go.Figure()

    # Add edge (Business Group to Product Family) - closer positioning
    fig.add_trace(go.Scatter(
        x=[0, 0.6], y=[0, -0.3], mode='lines', line=dict(width=2, color='white'),
        hoverinfo='text',
        text=['<b>Edge Attributes</b><br>' + '<br>'.join(edge)]  # Edge hover text
    ))

    # Add Business Group node (positioned at y=0)
    fig.add_trace(go.Scatter(
        x=[0], y=[0], mode='markers+text', marker=dict(size=15, color='cyan'),
        text=['Business Group'], textposition='top center', hoverinfo='text',
        hovertext='<b>Business Group</b><br>' + '<br>'.join(nodes['Business Group'])  # Attributes for hover
    ))

    # Add Product Family node (positioned at y=-0.3)
    fig.add_trace(go.Scatter(
        x=[0.6], y=[-0.3], mode='markers+text', marker=dict(size=15, color='orange'),
        text=['Product Family'], textposition='top center', hoverinfo='text',
        hovertext='<b>Product Family</b><br>' + '<br>'.join(nodes['Product Family'])  # Attributes for hover
    ))

    # Update layout for visibility
    fig.update_layout(
        title=dict(
            text="Business Group Schema",  # Title text
            x=0.5,  # Center the title
            xanchor='center',  # Horizontal alignment
            yanchor='top'  # Vertical alignment
        ),
        height=250,  # Reduce the height of the graph
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
    num_business_units = len(data)

    # Create a subplot layout with one plot per business unit
    fig = make_subplots(
        rows=1, cols=num_business_units,
        subplot_titles=[f"Business Unit {i+1}" for i in range(num_business_units)]
    )

    # Colors for each business unit
    colors = ['#2196F3', '#4CAF50', '#FF9800', '#9C27B0', '#FFC107', '#00BCD4', '#795548', '#607D8B']

    # Plot each business unit
    for i, d in enumerate(data):
        x_values = list(range(len(d)))

        # Add the line plot with shaded area
        fig.add_trace(
            go.Scatter(
                x=x_values,
                y=d,
                mode='lines',
                line=dict(color=colors[i], width=2),
                fill='tozeroy',  # Fill area under the line
                fillcolor=f"rgba({int(colors[i][1:3], 16)}, {int(colors[i][3:5], 16)}, {int(colors[i][5:], 16)}, 0.3)",
                name=f"Business Unit {i+1}"
            ),
            row=1, col=i+1
        )

    # Consistent y-axis limits
    max_y = max([max(bu) for bu in data]) * 1.1
    for i in range(1, num_business_units + 1):
        fig.update_yaxes(range=[0, max_y], title="Revenue", row=1, col=i)
        fig.update_xaxes(title="Time", row=1, col=i)

    # Customize layout with default Plotly styles
    fig.update_layout(
        title="Revenue Generated by Business Units Over Time",
        height=500,  # Increase height for better display
        width=600 * num_business_units,  # Dynamically adjust width for more space
        template="plotly_dark"  # Use dark mode theme
    )

    return fig


def plotly_ego_graph(ego_graph):
    """
    Visualizes the ego graph using Plotly, displaying node IDs as labels and attributes on hover.
    """
    pos = nx.spring_layout(ego_graph)
    
    # Edges
    edge_x = []
    edge_y = []
    edge_hover_text = []

    for edge in ego_graph.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.append(x0)
        edge_y.append(y0)
        edge_x.append(x1)
        edge_y.append(y1)
        edge_x.append(None)  # To separate edges visually
        edge_y.append(None)

        # Format hover text for edges
        attributes = edge[2]
        hover_details = [f"{key}: {value}" for key, value in attributes.items()]
        edge_hover_text.append("<br>".join(hover_details))

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=0.5, color="gray"),
        hoverinfo="text",
        hovertext=edge_hover_text,  # Show edge attributes on hover
        mode="lines"
    )

    # Nodes
    node_x = []
    node_y = []
    node_ids = []
    node_hover_text = []

    for node in ego_graph.nodes(data=True):
        x, y = pos[node[0]]
        node_x.append(x)
        node_y.append(y)
        node_ids.append(str(node[0]))  # Use node ID as label

        # Format hover text for nodes
        attributes = node[1]
        hover_details = [f"{key}: {value}" for key, value in attributes.items()]
        node_hover_text.append("<br>".join(hover_details))

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",  # Display labels with text
        text=node_ids,  # Node IDs as labels
        textposition="top center",
        hoverinfo="text",
        hovertext=node_hover_text,  # Show attributes on hover
        marker=dict(
            showscale=False,
            colorscale="YlGnBu",
            size=20,
            color=[1] * len(node_x),
        ),
    )

    layout = go.Layout(
        showlegend=False,
        hovermode="closest",
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False),
        height=300,
        margin=dict(l=80, r=40, t=30, b=20),  # Adjust margins
    )

    fig = go.Figure(data=[edge_trace, node_trace], layout=layout)
    return fig


@st.fragment
def ego(business_group_id):
    graph=st.session_state.temporal_graph.load_graph_at_timestamp(1)
    ego_graph = ego_graph_query(graph, business_group_id, 1)
    if ego_graph:
        st.write(f"### Neighbors for {business_group_id}")
        # st.write(f"Ego Graph for Node: {supplier_id}")
        # st.write(f"Nodes: {ego_graph.number_of_nodes()}, Edges: {ego_graph.number_of_edges()}")

        # Visualize and render the ego graph with Plotly
        fig = plotly_ego_graph(ego_graph)
        st.plotly_chart(fig)  # Display the figure in Streamlit


def ego_graph_query(graph, node_id, radius):
    """
    Returns the ego graph for a specific node within a given radius.
    """
    ego_graph = nx.ego_graph(graph, node_id, radius=radius)
    return ego_graph

    
def plot_higest_revenue(revenue, identifier, m):
    # Reduced size of the figure, keeping it proportional
    fig, ax = plt.subplots(figsize=(3, 3), facecolor='none')  # Adjusted figsize to reduce size
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
    
    # Hide the axis
    ax.axis('off')

    # Remove background and extra padding
    fig.patch.set_alpha(0)
    
    # Tight layout to reduce any extra space
    plt.tight_layout(pad=0.1)  # Minimized padding

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

    st.title("Business Group Dashboard")
    
    # Validate session state
    if "temporal_graph" not in st.session_state:
        st.error("No Temporal Graph found in the session state. Please run the main script first.")
        return

    highest_business_group = []  # Heap to store the highest business groups
    revenue_of_business_group_across_time = []
    totalTimeStamps = len(st.session_state.temporal_graph.files)
    
    for time in range(totalTimeStamps):
        data = st.session_state.temporal_graph.load_json_at_timestamp(time)
        business_nodes = data["node_values"]["BUSINESS_GROUP"]
        
        for i in range(len(business_nodes)):
            heapq.heappush(highest_business_group, (-business_nodes[i][-2], business_nodes[i][-1], time))
            if len(highest_business_group) > 3:
                heapq.heappop(highest_business_group)

            if len(revenue_of_business_group_across_time) < i + 1:
                revenue_of_business_group_across_time.append([])

            revenue_of_business_group_across_time[i].append(business_nodes[i][-2])
    
    # Display the top 3 business groups in columns
    cols = st.columns(len(highest_business_group)+1)
    with cols[0]:
        fig = create_graph()
        st.plotly_chart(fig, use_container_width=True)
    
    for i in range(len(highest_business_group)):
        revenue, identifier, month_index = heapq.heappop(highest_business_group)
        fig2 = plot_higest_revenue(-revenue, identifier, month_index)
        with cols[i+1]:
            st.pyplot(fig2)
    
    st.markdown("<hr style='margin-top: -50px; margin-bottom: -50px; border: none; border-top: 1px solid #ccc;' />", unsafe_allow_html=True)
    fig1 = plot_revenue(revenue_of_business_group_across_time)
    st.plotly_chart(fig1, use_container_width=True)


    st.divider()  
    timestamp = st.sidebar.slider("Select Timestamp", min_value=0, max_value=len(st.session_state.temporal_graph.files) - 1)
    node_details_input(business_nodes)


    st.text(" ")  # Adds one blank line
    st.text(" ")  # Adds another blank line

    st.divider()  # Adds a horizontal divider (thin line), visually separating sections
    
if __name__ == "__main__":
    main()