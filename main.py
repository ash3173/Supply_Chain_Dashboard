import streamlit as st
import glob
import re
from TemporalGraphClass import TemporalGraphClass 
import requests
from constants import getTimestamp, getdata

# Streamlit app starts here
def main():
    st.title("Temporal Graph Dashboard")

    # Specify the directory containing JSON files
    data_directory = "data/supply_chain_export_100/"
    files = glob.glob(f"{data_directory}timestamp_*.json")

    if not files:
        st.error("No JSON files found in the specified directory.")
        return
    
    data = requests.get(getTimestamp).json()
    totalTimeStamps = len(data)

    files = []
    for i in range(1,totalTimeStamps+1) :
        files.append(f"{getdata}/{i}")
    
    # Initialize TemporalGraph
    temporal_graph = TemporalGraphClass(files)   
    if temporal_graph not in st.session_state:
        st.session_state.temporal_graph = temporal_graph 

    # Success message
    st.success("Files processed successfully!")

if __name__ == "__main__":
    main()