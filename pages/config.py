# Monkey-patch as early as possible
from gevent import monkey
monkey.patch_all()
import importlib
import os
import time
import logging
import streamlit as st
import subprocess
from locust import HttpUser, task, between, events
import subprocess
ordered_filenames = [
    '1_Business_Group',
    '6_Parts',
    '2_Product_Family',
    '3_Product_Offering',
    '5_Warehouse',
    '7_Supplier'
]

# Import modules dynamically and store in a dictionary
modules = {name: importlib.import_module(f'pages.{name}') for name in ordered_filenames}

# Access attributes from the modules
bg_static_part = modules['1_Business_Group'].static_part
bg_node_details_input = modules['1_Business_Group'].node_details_input
bg_create_graph = modules['1_Business_Group'].create_graph

p_static_part = modules['6_Parts'].static_part
p_node_details_input = modules['6_Parts'].node_details_input
p_queries = modules['6_Parts'].queries

pf_static_part = modules['2_Product_Family'].static_part
pf_node_details_input = modules['2_Product_Family'].node_details_input
pf_create_graph = modules['2_Product_Family'].create_graph

po_static_part = modules['3_Product_Offering'].static_part
po_node_details_input = modules['3_Product_Offering'].node_details_input
po_queries = modules['3_Product_Offering'].queries

w_static_part = modules['5_Warehouse'].static_part
w_node_details_input = modules['5_Warehouse'].node_details_input
w_create_graph = modules['5_Warehouse'].create_graph

sup_static_part = modules['7_Supplier'].static_part
sup_node_details_input = modules['7_Supplier'].node_details_input
sup_queries = modules['7_Supplier'].queries
logging.basicConfig(level=logging.INFO)

class BG(HttpUser):
    wait_time = between(1, 5)
    host = "http://localhost"  # Dummy host to satisfy Locust's requirement
    
    def on_start(self):
        self.start_time = time.time()
    
    def on_stop(self):
        end_time = time.time()
        total_time = end_time - self.start_time
        user_count = self.environment.runner.user_count
        logging.info(f"Total time for test: {total_time} seconds, Number of users: {user_count}")
    
    def log_event(self, request_type, name, start_time, result=None, exception=None):
        end_time = time.time()
        response_time = (end_time - start_time) * 1000  # Convert to milliseconds
        response_length = len(result) if isinstance(result, (list, str)) else 0
        
        if exception:
            events.request.fire(request_type=request_type, name=name, response_time=response_time, response_length=response_length, exception=exception)
            logging.error(f"Error: {exception}, Time taken: {response_time} ms")
        else:
            events.request.fire(request_type=request_type, name=name, response_time=response_time, response_length=response_length)
            logging.info(f"Result: {result}, Time taken: {response_time} ms")
    
    @task
    def test_bg_static_part(self):
        start_time = time.time()
        try:
            result = bg_static_part()
            self.log_event("Business_Group", "bg_static_part", start_time, result)
        except Exception as e:
            self.log_event("Business_Group", "bg_static_part", start_time, exception=e)

    @task
    def test_p_static_part(self):
        start_time = time.time()
        try:
            result = p_static_part()
            self.log_event("Parts", "p_static_part", start_time, result)
        except Exception as e:
            self.log_event("Parts", "p_static_part", start_time, exception=e)
    
    @task
    def test_node_details_input(self):
        start_time = time.time()
        try:
            result = bg_node_details_input()
            self.log_event("Business_Group", "bg_node_details_input", start_time, result)
        except Exception as e:
            self.log_event("Business_Group", "bg_node_details_input", start_time, exception=e)
    
    @task
    def test_create_graph(self):
        start_time = time.time()
        try:
            result = bg_create_graph()
            self.log_event("Business_Group", "bg_create_graph", start_time, result)
        except Exception as e:
            self.log_event("Business_Group", "bg_create_graph", start_time, exception=e)

class Parts(HttpUser):
    wait_time = between(1, 5)
    host = "http://localhost"  # Dummy host to satisfy Locust's requirement
    
    def on_start(self):
        self.start_time = time.time()
    
    def on_stop(self):
        end_time = time.time()
        total_time = end_time - self.start_time
        user_count = self.environment.runner.user_count
        logging.info(f"Total time for test: {total_time} seconds, Number of users: {user_count}")
    
    def log_event(self, request_type, name, start_time, result=None, exception=None):
        end_time = time.time()
        response_time = (end_time - start_time) * 1000  # Convert to milliseconds
        response_length = len(result) if isinstance(result, (list, str)) else 0
        
        if exception:
            events.request.fire(request_type=request_type, name=name, response_time=response_time, response_length=response_length, exception=exception)
            logging.error(f"Error: {exception}, Time taken: {response_time} ms")
        else:
            events.request.fire(request_type=request_type, name=name, response_time=response_time, response_length=response_length)
            logging.info(f"Result: {result}, Time taken: {response_time} ms")
    
    @task
    def test_bg_static_part(self):
        start_time = time.time()
        try:
            result = bg_static_part()
            self.log_event("Business_Group", "bg_static_part", start_time, result)
        except Exception as e:
            self.log_event("Business_Group", "bg_static_part", start_time, exception=e)

    @task
    def test_p_static_part(self):
        start_time = time.time()
        try:
            result = p_static_part()
            self.log_event("Parts", "p_static_part", start_time, result)
        except Exception as e:
            self.log_event("Parts", "p_static_part", start_time, exception=e)
    
    @task
    def test_node_details_input(self):
        start_time = time.time()
        try:
            result = bg_node_details_input()
            self.log_event("Business_Group", "bg_node_details_input", start_time, result)
        except Exception as e:
            self.log_event("Business_Group", "bg_node_details_input", start_time, exception=e)
    
    @task
    def test_create_graph(self):
        start_time = time.time()
        try:
            result = bg_create_graph()
            self.log_event("Business_Group", "bg_create_graph", start_time, result)
        except Exception as e:
            self.log_event("Business_Group", "bg_create_graph", start_time, exception=e)



def load_test_page():
    st.title("Load Test with Locust")
    class_name=["BG","Parts"]
    selected_class = st.selectbox("Select a script to run", class_name)
    if st.button("Run Load Test"):
        with st.spinner("Starting Locust..."):
            # command = ["locust", "-f", "config.py", "--user-class", BG]
            # command="locust -f config.py --user-class BG"
            # process = subprocess.Popen(command)
            process = subprocess.Popen(["locust", "-f", "D:\Class Textbook\Sem5\Querying\Supply_Chain_Dashboard\pages\config.py","BG"])

            st.session_state["locust_process"] = process
            st.success("Locust is starting. Please wait...")
            
            if process.poll() is None:
                st.success("Locust is running. You can access the web interface at http://localhost:8089")
            else:
                st.error("Failed to start Locust.")
    if "locust_process" in st.session_state and st.button("Kill Locust Process"):
        locust_process = st.session_state["locust_process"]
        locust_process.terminate()
        st.success("Locust process terminated.")
    st.write("Once the Locust server is running, you can access the web interface at:")
    st.code("http://localhost:8089")
    st.write("Use the web interface to start and monitor your load tests.")

if __name__ == "__main__":
    load_test_page()

