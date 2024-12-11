import streamlit as st
import time
import tracemalloc
import psutil
import multiprocessing
import os

# # Set page configuration
# st.set_page_config(
#     page_title="Stress Test Dashboard",
#     page_icon="🚀",
#     layout="wide",
#     initial_sidebar_state="expanded",
# )

from pages.Business_Group import (
   static_part as bg_static_part,
   node_details_input as bg_node_details_input,
   create_graph as bg_create_graph
)
from pages.Parts_copy import(
    static_part as p_static_part,   
    node_details_input as p_node_details_input,   
    queries as p_queries
)
from pages.Product_Family_copy import(
    static_part as pf_static_part,
    node_details_input as pf_node_details_input,
    create_graph as pf_create_graph
)
from pages.Product_Offering_copy import(
    static_part as po_static_part,
    node_details_input as po_node_details_input,
    queries as po_queries
)
from pages.Warehouse_copy import(
    static_part as w_static_part,   
    node_details_input as w_node_details_input,   
    create_graph as w_create_graph
)
from pages.Supplier_copy import(
    static_part as sup_static_part,
    node_details_input as sup_node_details_input,
    queries as sup_queries
)
#add facility later

class PageStressTester:
   def __init__(self):
       # Initialize test data
       timestamp = 2
       self.test_data = {
           'timestamp_range': (0, 14),
           'graph': st.session_state.temporal_graph.load_graph_at_timestamp(timestamp),
           'node_index': {},
           'business_group_id': "BG_001"
       }
       
       self.pages = {
           "Business Group": {
               'functions': [
                   bg_static_part,
                   bg_node_details_input,
                   bg_create_graph
               ]
           },
            "Parts":{
               'functions': [
                   p_static_part,
                   p_node_details_input,
                   p_queries
               ]
           },
            "Product Family":{
               'functions': [
                   pf_static_part,
                   pf_node_details_input,
                   pf_create_graph
               ]
           },
           "Product Offering":{
               'functions': [
                   po_static_part,
                   po_node_details_input,
                   po_queries
               ]
           },
            "Warehouse":{
               'functions': [
                   w_static_part,
                   w_node_details_input,
                   w_create_graph
               ]
           },
            "Supplier":{
               'functions': [
                   sup_static_part,
                   sup_node_details_input,
                   sup_queries
               ]
           }
       }

   def test_single_function(self, func):
       """Test a single function with performance metrics"""
       tracemalloc.start()
       process = psutil.Process(os.getpid())
       initial_cpu = process.cpu_percent()
       start_time = time.time()
       
       try:
           result = func()
           status = "success"
           error = None
       except Exception as e:
           result = None
           status = "error"
           error = str(e)
       
       end_time = time.time()
       current, peak = tracemalloc.get_traced_memory()
       cpu_usage = process.cpu_percent() - initial_cpu
       tracemalloc.stop()
       
       return {
           'status': status,
           'execution_time': end_time - start_time,
           'memory_current': current / 1024 / 1024,  # MB
           'memory_peak': peak / 1024 / 1024,  # MB
           'cpu_usage': cpu_usage,
           'error': error,
           'function': func.__name__
       }

   def test_all_functions(self, functions):
       """Test all functions together with combined performance metrics"""
       tracemalloc.start()
       process = psutil.Process(os.getpid())
       initial_cpu = process.cpu_percent()
       start_time = time.time()
       
       results = []
       try:
           for func in functions:
               try:
                   result = func()
                   results.append({"function": func.__name__, "status": "success"})
               except Exception as e:
                   results.append({
                       "function": func.__name__,
                       "status": "error",
                       "error": str(e)
                   })
           
           overall_status = "success" if all(r["status"] == "success" for r in results) else "partial_success"
           
       except Exception as e:
           overall_status = "error"
           results.append({"status": "error", "error": str(e)})
       
       end_time = time.time()
       current, peak = tracemalloc.get_traced_memory()
       cpu_usage = process.cpu_percent() - initial_cpu
       tracemalloc.stop()
       
       return {
           'overall_status': overall_status,
           'execution_time': end_time - start_time,
           'memory_current': current / 1024 / 1024,
           'memory_peak': peak / 1024 / 1024,
           'cpu_usage': cpu_usage,
           'function_results': results
       }

   def run_page_test(self, page_name, test_mode="individual"):
       """Run stress test for a page in specified mode"""
       if page_name not in self.pages:
           return {"status": "error", "message": f"Page {page_name} not found"}
       
       page_info = self.pages[page_name]
       
       if test_mode == "individual":
           individual_results = []
           for func in page_info['functions']:
               result = self.test_single_function(func)
               individual_results.append(result)
           return {
               "mode": "individual",
               "results": individual_results
           }
       else:  # comprehensive mode
           return {
               "mode": "comprehensive",
               "results": self.test_all_functions(page_info['functions'])
           }

def stress_test_selected_page(page, num_cores, test_mode):
    st.session_state.stress_testing = True
    tester = PageStressTester()
    results = []

    try:
        result = tester.run_page_test(page, test_mode)
        results.append({
            "page": page,
            "results": result
        })
    finally:
        st.session_state.stress_testing = False

    return {
        'page_results': results,
        'total_pages_tested': 1,
        'cores_used': num_cores,
        'test_mode': test_mode
    }

def display_individual_metrics(metrics):
   """Display metrics for individual function test"""
   status_color = "green" if metrics["status"] == "success" else "red"
   st.markdown(f"### Function: {metrics['function']}")
   st.markdown(f"Status: :{status_color}[{metrics['status']}]")
   
   col1, col2 = st.columns(2)
   with col1:
       st.metric("Execution Time", f"{metrics['execution_time']:.3f}s")
       st.metric("CPU Usage", f"{metrics['cpu_usage']:.1f}%")
   
   with col2:
       st.metric("Memory Current", f"{metrics['memory_current']:.1f}MB")
       st.metric("Memory Peak", f"{metrics['memory_peak']:.1f}MB")
   
   if metrics.get("error"):
       st.error(f"Error: {metrics['error']}")

def display_comprehensive_metrics(metrics):
   """Display combined metrics for all functions"""
   st.subheader("Combined Performance Metrics")
   
   col1, col2 = st.columns(2)
   with col1:
       st.metric("Total Execution Time", f"{metrics['execution_time']:.3f}s")
       st.metric("CPU Usage", f"{metrics['cpu_usage']:.1f}%")
   
   with col2:
       st.metric("Memory Current", f"{metrics['memory_current']:.1f}MB")
       st.metric("Memory Peak", f"{metrics['memory_peak']:.1f}MB")
   
   st.subheader("Individual Function Results")
   for result in metrics['function_results']:
       status_color = "green" if result["status"] == "success" else "red"
       st.markdown(f"**{result['function']}**: :{status_color}[{result['status']}]")
       if result.get("error"):
           st.error(f"Error: {result['error']}")

def main():
    # Configuration section
    col1, col2, col3 = st.columns(3)

    with col1:
        total_cores = multiprocessing.cpu_count()
        num_cores = st.selectbox(
            "Select number of CPU cores",
            options=range(1, total_cores + 1),
            help="Select number of cores for testing"
        )

    with col2:
        available_pages = ["Business Group", "Parts", "Product Family", "Product Offering", "Warehouse", "Supplier"]
        selected_page = st.selectbox(
            "Select a page to test",
            available_pages,
            index=0  # Default selection is "Business Group"
        )

    with col3:
        test_mode = st.radio(
            "Select test mode",
            ["individual", "comprehensive"],
            help="Individual: Test each function separately\nComprehensive: Test all functions together"
        )

    if st.button("Run Stress Test", type="primary"):
        if not selected_page:
            st.warning("Please select at least one page to test.")
            return

        # Debugging print to check selected page
        print(f"Selected page: {selected_page}")

        with st.spinner("Running stress tests..."):
            results = stress_test_selected_page(selected_page, num_cores, test_mode)

            # Display results
            st.header("Test Results")

            for page_result in results['page_results']:
                st.subheader(f"{page_result['page']} Results")
                print(page_result)  # Check the entire dictionary
                print(page_result.get('results'))  # Check the 'results' key

                # Check if 'results' key exists in page_result
                if 'results' in page_result:
                    if results.get('test_mode') == "individual":
                        for metric in page_result['results']['results']:
                            display_individual_metrics(metric)
                    else:
                        display_comprehensive_metrics(page_result['results']['results'])
                else:
                    st.error(f"No 'results' key found in page_result for {page_result['page']}")


if __name__ == "__main__":
   main()