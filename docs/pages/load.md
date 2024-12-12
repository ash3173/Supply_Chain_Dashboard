# Load Test Documentation

## Overview

This documentation provides insights into the functionality of the provided Python script for load testing, the technologies it uses, and its relevance to a supply chain environment. It also explains how to use the Locust framework for testing.

---

## Technology Used

- **Python**: The core programming language used for implementing the script.
- **Locust**: A load testing framework used to simulate multiple users and test system performance under load.
- **Streamlit**: A web-based framework used for building the user interface to manage the load test.
- **Gevent**: A library for asynchronous I/O operations, improving performance by enabling non-blocking tasks.
- **Subprocess**: Used to manage external Locust processes.
- **Logging**: For tracking events, errors, and performance metrics during the tests.

---

## Goal of the Page

The main goal of this script is to facilitate load testing of various components in a supply chain system by simulating user interactions and recording system performance. This helps identify bottlenecks and optimize system reliability.

---

## What is a Load Test?

Load testing is the process of putting demand on a system and measuring its response. It evaluates how the system performs under expected or peak user loads to ensure it can handle real-world scenarios.

---

## Explanation of the Code

### Classes and Functions

#### 1. **`QueryUser` Class**
   - A subclass of `HttpUser` in the Locust framework.
   - Simulates user interactions with various endpoints.
   - Contains tasks (methods) that are executed to test different system functionalities.

   ##### Key Methods:
   - **`on_start` and `on_stop`**: Tracks the start and stop times for a test session.
   - **`log_event`**: Logs the results of each request, including response time, length, and exceptions.
   - **Various @task methods**: Each method tests a specific function from the imported modules, such as:
     - `bg_static_part`: Tests static parts of the "Business Group" module.
     - `p_node_details_input`: Tests node details input for "Parts".
     - `sup_queries`: Tests queries related to "Suppliers".

#### 2. **`load_test_page` Function**
   - Creates a Streamlit-based UI to manage Locust processes.
   - **Key Features**:
     - Button to start Locust and monitor it via the web interface.
     - Button to terminate the Locust process.
     - Displays the Locust UI link for user interactions.

---

## Locust Framework

Locust is an open-source load testing framework that allows simulating millions of users interacting with a system. Users can define tasks that represent user behavior, and Locust monitors system performance, including:

- **Response Time**: Measures how long it takes for the system to respond to a request.
- **Number of Users**: The total number of simulated users in the test.
- **Percentile**: Shows performance metrics at different percentiles (e.g., 95th percentile indicates that 95% of requests are faster than this time).

---

## How to Run on Localhost

1. Install dependencies using `pip install locust streamlit gevent`.
2. Run the script in the terminal:
   ```bash
   python Load_test.py
   ```
3. Access the Streamlit interface in the browser:
   ```
   http://localhost:8501
   ```
4. Start Locust from the Streamlit UI. The Locust web interface will be available at:
   ```
   http://localhost:8089
   ```
5. Configure user count and spawn rate in the Locust UI to start the load test.

---

## Relevance to Supply Chain

- **Performance Monitoring**: Ensures supply chain systems handle high demand efficiently.
- **Reliability Testing**: Identifies and resolves bottlenecks in critical operations like product offering, warehouse management, and supplier integration.
- **Scalability**: Helps plan infrastructure upgrades based on performance under load.

---

## Key Metrics in Locust UI

- **Response Time**: Time taken by the server to handle a request.
- **Number of Users**: Current active virtual users simulating traffic.
- **Percentiles**:
  - **50th**: Median response time.
  - **95th**: Time within which 95% of requests are completed.
  - **99th**: Time within which 99% of requests are completed.

---

## Summary

This script provides a robust and modular way to test the performance of supply chain systems under load. Using Locust, the script enables scalable, real-world testing scenarios, making it essential for ensuring reliability and efficiency in supply chain management.

