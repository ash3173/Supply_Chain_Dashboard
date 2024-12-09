import streamlit as st
from TemporalGraphClass import TemporalGraphClass 
import requests
from dotenv import load_dotenv
import os
import json
import glob

load_dotenv()
base_url = os.getenv("base_url")
version = os.getenv("version")
getVersions = os.getenv("getVersions")
getdata = f"{base_url}/archive/schema/{version}"
getTimestamp = f"{base_url}/archive/schema/{version}"

data_folder = "data"    

# Streamlit app starts here
# main for running from server
def main():
    st.title("Temporal Graph Dashboard")
    st.write("Selected Version", version)

    target_path = os.path.join(data_folder, version)
    if os.path.exists(target_path) and os.path.isdir(target_path):
        st.write("Version exists")
        all_files = [f for f in os.listdir(target_path) if os.path.isfile(os.path.join(target_path, f))]
        all_timestamps = requests.get(getTimestamp).json()

        for timestamp in all_timestamps:
            if f"{timestamp}.json" not in all_files:
                timestamp_data = requests.get(f"{getdata}/{timestamp}").json()
                with open(os.path.join(target_path, f"{timestamp}.json"), "w") as f:
                    json.dump(timestamp_data, f, indent=4)

    else:
        st.write("Version doesnt exist")
        os.makedirs(target_path)
        all_timestamps = requests.get(getTimestamp).json()

        for timestamp in all_timestamps:
            timestamp_data = requests.get(f"{getdata}/{timestamp}").json()
            with open(os.path.join(target_path, f"{timestamp}.json"), "w") as f:
                json.dump(timestamp_data, f, indent=4)

    all_files = [os.path.join(target_path,f) for f in os.listdir(target_path) if os.path.isfile(os.path.join(target_path, f))]
    all_files.sort(key = lambda x: int(x.split("\\")[-1].split(".")[0]))

    # Initialize TemporalGraph
    temporal_graph = TemporalGraphClass(all_files)   
    if temporal_graph not in st.session_state:
        st.session_state.temporal_graph = temporal_graph 

    # Success message
    st.success("Files processed successfully!")

if __name__ == "__main__":
    main()