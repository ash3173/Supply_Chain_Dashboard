from gevent import monkey
monkey.patch_all()
import importlib
import os
import time
import logging
import streamlit as st
import subprocess
from locust import HttpUser, task, between, events
ordered_filenames = [
    '1_Business_Group',
    '6_Parts',
    '2_Product_Family',
    '3_Product_Offering',
    '4_Facility',
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

f_static_part = modules['4_Facility'].static_part
f_node_details_input = modules['4_Facility'].node_details_input
f_create_graph = modules['4_Facility'].create_graph

w_static_part = modules['5_Warehouse'].static_part
w_node_details_input = modules['5_Warehouse'].node_details_input
w_create_graph = modules['5_Warehouse'].create_graph

sup_static_part = modules['7_Supplier'].static_part
sup_node_details_input = modules['7_Supplier'].node_details_input
sup_queries = modules['7_Supplier'].queries
logging.basicConfig(level=logging.INFO)

class QueryUser(HttpUser):
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
    def test_p_node_details_input(self):
        start_time = time.time()
        try:
            result = p_node_details_input()
            self.log_event("Parts", "p_node_details_input", start_time, result)
        except Exception as e:
            self.log_event("Parts", "p_node_details_input", start_time, exception=e)    
    @task
    def test_p_queries(self):
        start_time = time.time()
        try:
            result = p_queries()
            self.log_event("Parts", "p_queries", start_time, result)
        except Exception as e:
            self.log_event("Parts", "p_queries", start_time, exception=e)
    
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
    
    
    @task
    def test_pf_static_part(self):
        start_time = time.time()
        try:
            logging.info("Calling pf_static_part function")
            result = pf_static_part()
            self.log_event("Product_Family", "pf_static_part", start_time, result)
        except Exception as e:
            self.log_event("Product_Family", "pf_static_part", start_time, exception=e)
    @task
    def test_pf_node_details_input(self):
        start_time = time.time()
        try:
            logging.info("Calling pf_node_detsils_input function")
            result = pf_node_details_input()
            self.log_event("Product_Family", "pf_node_details_input", start_time, result)
        except Exception as e:
            self.log_event("Product_Family", "pf_node_details_input", start_time, exception=e)

    @task
    def test_pf_create_graph(self):
        start_time = time.time()
        try:
            logging.info("Calling pf_create_graph function")
            result = pf_node_details_input()
            self.log_event("Product_Family", "pf_create_graph", start_time, result)
        except Exception as e:
            self.log_event("Product_Family", "pf_create_graph", start_time, exception=e)

    @task
    def test_po_static_part(self):
        start_time = time.time()
        try:
            logging.info("Calling po_static_part function")
            result = po_static_part()
            self.log_event("Product_Offering", "po_static_part", start_time, result)
        except Exception as e:
            self.log_event("Product_Offering", "po_static_part", start_time, exception=e)
    
    @task
    def test_po_node_details_input(self):
            start_time = time.time()
            try:
                logging.info("Calling po_node_details_input function")
                result = po_node_details_input()
                self.log_event("Product_Offering", "po_node_details_input", start_time, result)
            except Exception as e:
                self.log_event("Product_Offering", "po_node_details_input", start_time, exception=e)
    @task
    def test_po_queries(self):    
            start_time = time.time()
            try:
                logging.info("Calling po_queries function")
                result = po_queries()
                self.log_event("Product_Offering", "po_queries", start_time, result)
            except Exception as e:
                self.log_event("Product_Offering", "po_queries", start_time, exception=e)

    @task
    def test_w_static_part(self):
        start_time = time.time()
        try:
            logging.info("Calling w_static_part function")
            result = w_static_part()
            self.log_event("Warehouse", "w_static_part", start_time, result)
        except Exception as e:
            self.log_event("Warehouse", "w_static_part", start_time, exception=e)
    @task
    def test_w_node_details_input(self):
            start_time = time.time()
            try:
                logging.info("Calling w_static_part function")
                result = w_node_details_input()
                self.log_event("Warehouse", "w_node_details_input", start_time, result)
            except Exception as e:
                self.log_event("Warehouse", "w_node_details_input", start_time, exception=e)

    @task
    def test_w_create_graph(self):
        start_time = time.time()
        try:
                logging.info("Calling w_create_graph function")
                result = w_node_details_input()
                self.log_event("Warehouse", "w_create_graph", start_time, result)
        except Exception as e:
            self.log_event("Warehouse", "w_create_graph", start_time, exception=e)

    @task
    def test_f_static_part(self):    
        start_time = time.time()
        try:
                logging.info("Calling f_static_part function")
                result = w_node_details_input()
                self.log_event("Facility", "f_static_part", start_time, result)
        except Exception as e:
            self.log_event("Facility", "f_static_part", start_time, exception=e)
    
    @task
    def test_f_node_details_input(self):        
        start_time = time.time()
        try:
                logging.info("Calling f_create_graph function")
                result = w_node_details_input()
                self.log_event("Facility", "f_create_graph", start_time, result)
        except Exception as e:
            self.log_event("Facility", "f_create_graph", start_time, exception=e)
    
    @task
    def test_f_create_graph(self):
        start_time = time.time()
        try:
                logging.info("Calling f_create_graph function")
                result = w_node_details_input()
                self.log_event("Facility", "f_create_graph", start_time, result)
        except Exception as e:
            self.log_event("Facility", "f_create_graph", start_time, exception=e)

    @task
    def test_sup_static_part(self):
        start_time = time.time()
        try:
            logging.info("Calling sup_static_part function")
            result = sup_static_part()
            self.log_event("Supplier", "sup_static_part", start_time, result)
        except Exception as e:
            self.log_event("Supplier", "sup_static_part", start_time, exception=e)
    @task
    def test_sup_node_details_input(self):
            start_time = time.time()
            try:
                logging.info("Calling sup_static_part function")
                result = sup_node_details_input()
                self.log_event("Supplier", "sup_node_details_input", start_time, result)
            except Exception as e:
                self.log_event("Supplier", "sup_node_details_input", start_time, exception=e)
    @task
    def test_sup_queries(self):
        start_time = time.time()
        try:
            logging.info("Calling sup_queries function")
            result = sup_queries()
            self.log_event("Supplier", "sup_queries", start_time, result)
        except Exception as e:
            self.log_event("Supplier", "sup_queries", start_time, exception=e)

def load_test_page():
    st.title("Load Test with Locust")
    
    if st.button("Run Load Test"):
        with st.spinner("Starting Locust..."):
            process = subprocess.Popen(["locust", "-f", r"C:\Users\HP\LAM_VS\Dashboard3\Supply_Chain_Dashboard\pages\Load_test.py"])
            
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
