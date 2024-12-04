import streamlit as st
from TemporalGraphClass import TemporalGraphClass 
import requests
from dotenv import load_dotenv
import os

import glob

load_dotenv()

getdata = os.getenv("GET_DATA")
getTimestamp = os.getenv("GET_TIMESTAMP")

# Streamlit app starts here
# main for running from server
def main():
    st.title("Temporal Graph Dashboard")
    
    data = requests.get(getTimestamp).json()
    totalTimeStamps = len(data)

    files = []
    for i in range(1,totalTimeStamps+1) :
        files.append(f"{getdata}/{i}")
    
    # Initialize TemporalGraph
    temporal_graph = TemporalGraphClass(files)   
    if temporal_graph not in st.session_state:
        st.session_state.temporal_graph = temporal_graph 

    st.write(st.session_state.temporal_graph.files[2])
    # Success message
    st.success("Files processed successfully!")

# # main for running locally
# def main() :
#     st.title("Temporal Graph Dashboard")
    
#     data_directory = "data"
#     files = glob.glob(f"{data_directory}/*.json")

#     if not files :
#         st.error("No files found in the data directory")
#         return
    
#     # Initialize TemporalGraph
#     temporal_graph = TemporalGraphClass(files)
#     if temporal_graph not in st.session_state:
#         st.session_state.temporal_graph = temporal_graph

#     # st.write(st.session_state.temporal_graph.files)

#     # Success message
#     st.success("Files processed successfully!")

if __name__ == "__main__":
    main()