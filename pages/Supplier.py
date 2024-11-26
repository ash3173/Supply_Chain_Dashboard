import streamlit as st
import json
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
    )


def get_visualization(data):
    supplier_data = data["node_values"]["Supplier"]
    place_freq = {}
    items_freq = {}

    for i in supplier_data:
        place = i[2]
        if place in place_freq:
            place_freq[place] += 1
        else:
            place_freq[place] = 1

        for items in i[6]:
            if items in items_freq:
                items_freq[items] += 1
            else:
                items_freq[items] = 1

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

    # Create a DataFrame and add state abbreviations
    df = pd.DataFrame(place_freq.items(), columns=['State', 'Value'])
    df['State_Abbreviation'] = df['State'].map(state_abbreviations)

    # Create the choropleth map
    fig1 = px.choropleth(
        df,
        locations='State_Abbreviation',  # Use abbreviations
        locationmode="USA-states",       # Use USA states mode
        color='Value',                   # Column to determine color
        scope="usa",                     # Focus on USA
        color_continuous_scale="Blues",  # Color scale
        labels={'Value': 'Supplier Count'}, # Customize label
        title='Concentration of Suppliers'

    )

    # Update layout for better appearance
    fig1.update_layout(
        title=dict(
        text='Concentration of Suppliers',
        x=0.5,  # Center the title
        xanchor='center',  # Align to center horizontally
        yanchor='top'  # Align vertically at the top
        ),
    
        template='plotly_dark',
        geo=dict(
            showlakes=True,  # Show lakes
            lakecolor='rgb(255, 255, 255)'  # Lake color
        ),
        # Set transparent background
        plot_bgcolor='rgba(0,0,0,0)',  # Transparent plot area
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent paper area
        font=dict(color="black"),        # Optional: Set font color
        # height=350
    )

    # Create the bar chart with blue color
    df = pd.DataFrame.from_dict(items_freq, orient='index', columns=['Frequency'])
    df = df.reset_index().rename(columns={'index': 'Item'})
    fig2 = px.bar(df, x='Item', y='Frequency', title='Number of suppliers per item')
    fig2.update_traces(marker_color='#ADD8E6')

    # Center the title
    fig2.update_layout(
        title=dict(
            text='Number of suppliers per item',
            x=0.5,  # Center the title
            xanchor='center',  # Align to center horizontally
            yanchor='top'  # Align vertically at the top
        )
    )

    return [fig1, fig2,supplier_data]



def create_graph():
    # Define node attributes for Supplier and Warehouse
    nodes = {
        'Supplier': ['node_type', 'name', 'location', 'reliability', 'size', 'size_category', 'supplied_part_types', 'id'],
        'Warehouse': ['node_type', 'name', 'type', 'location', 'size_category', 'max_capacity', 'current_capacity', 'safety_stock', 'max_parts', 'id']
    }
    edge = ['relationship_type', 'transportation_cost', 'lead_time', 'source', 'target']

    # Create a new figure
    fig = go.Figure()

    # Add edge (Supplier to Warehouse) - vertically aligned
    fig.add_trace(go.Scatter(
        x=[0, 1], y=[0, -1], mode='lines', line=dict(width=2, color='white'),
        hoverinfo='text',
        text=['<b>Edge Attributes</b><br>' + '<br>'.join(edge)]  # Edge hover text formatted line-by-line
    ))

    # Add Supplier node (positioned at y=0)
    fig.add_trace(go.Scatter(
        x=[0], y=[0], mode='markers+text', marker=dict(size=20, color='cyan'),
        text=['Supplier'], textposition='top center', hoverinfo='text',
        hovertext='<b>Supplier</b><br>' + '<br>'.join(nodes['Supplier'])  # Show only attribute names
    ))

    # Add Warehouse node (positioned at y=-1)
    fig.add_trace(go.Scatter(
        x=[1], y=[-1], mode='markers+text', marker=dict(size=20, color='orange'),
        text=['Warehouse'], textposition='top center', hoverinfo='text',
        hovertext='<b>Warehouse</b><br>' + '<br>'.join(nodes['Warehouse'])  # Show only attribute names
    ))

    # Update layout for dark mode, transparent background, and properly formatted hover text
    fig.update_layout(
        title=dict(
        text="Supplier Schema",  # Title text
        x=0.5,  # Center the title
        xanchor='center',  # Horizontal alignment
        yanchor='top'  # Vertical alignment
    ),  showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        font=dict(color="white"),  # White text color
        hoverlabel=dict(bgcolor="black", font_color="white"),  # Hover label styling
        plot_bgcolor='rgba(0,0,0,0)',  # Transparent background
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent paper background
    )

    return fig


def main():

    st.markdown("""
    <style>
    
           /* Remove blank space at top and bottom */ 
           .block-container {
               padding-top: 0rem;
               padding-bottom: 0rem;
            }
           
           /* Remove blank space at the center canvas */ 
           .st-emotion-cache-z5fcl4 {
               position: relative;
               top: -50px;
               }
           
           /* Make the toolbar transparent and the content below it clickable */ 
           .st-emotion-cache-18ni7ap {
               pointer-events: none;
               background: rgb(255 255 255 / 0%)
               }
           .st-emotion-cache-zq5wmm {
               pointer-events: auto;
               background: rgb(255 255 255);
               border-radius: 5px;
               }
    </style>
    """, unsafe_allow_html=True)
    

    st.title("Supplier Dashboard")
    if "temporal_graph" not in st.session_state:
        st.error("No Temporal Graph found in the session state. Please run the main script first.")
        return

    timestamp = 2

    # Load the JSON data at the given timestamp
    with open(st.session_state.temporal_graph.files[timestamp], 'r') as f:
        data = json.load(f)

    col1, col2, col3 = st.columns([1,4,2], gap='medium')

    with col1:
        fig = create_graph()
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig1, fig2,supplier_data = get_visualization(data)
        st.plotly_chart(fig1, use_container_width=True)  # Display figure 1

    with col3:
        st.plotly_chart(fig2, use_container_width=True)  # Display figure 2

    col1, col2=st.columns(2)


    with col1:
        st.write("Supplier ID Info")
        
        # Input field for Supplier ID
        supplier_id = st.text_input("Enter Supplier ID:")

        # Display the properties if the Supplier ID is valid
        for val in supplier_data:
            if supplier_id in val:
                st.write("### Node Properties")
                attributes = [
                    "Node Type", "Name", "Location", "Reliability", "Size", "Size Category", 
                    "Supplied Part Types", "ID"
                ]
                

                # Display each attribute and its value
                for attr, value in zip(attributes, val):
                    st.write(f"**{attr}:** {value}")
                break

            
    with col2:
        st.write("Ego")

        

if __name__ == "__main__":
    main()