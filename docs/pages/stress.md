# Stress Test Dashboard Documentation

## Technologies Used

- **Python Standard Libraries**:
  - `time`: For measuring execution time.
  - `tracemalloc`: For memory tracking during function execution.
  - `psutil`: For monitoring CPU usage and system processes.
  - `multiprocessing`: For determining available CPU cores.
  - `os`: For process management.
  - `importlib`: For dynamic module import.

## Goal of the Code

The purpose of this code is to implement a **stress testing dashboard** that evaluates the performance of different functions across various pages of a web application. Stress testing involves assessing the application’s behavior under high loads, measuring resource usage, and identifying potential bottlenecks or errors.

## What is a Stress Test?

A **stress test** is a performance testing technique used to determine an application’s robustness and stability under extreme conditions. It identifies potential points of failure and measures how the application behaves under increased load, resource constraints, or other high-stress scenarios.

### How Stress Testing Works (Simple Explanation)

1. **Execution**: Each function or a group of functions is executed.
2. **Monitoring**: Metrics like execution time, memory usage, and CPU usage are collected.
3. **Error Handling**: Errors are captured and logged.
4. **Evaluation**: Results are analyzed to determine if the system meets performance expectations.

---

## Explanation of Each Function

### 1. `test_single_function(func)`
- **Description**: Executes a single function and captures its performance metrics.
- **Key Steps**:
  - Starts memory tracking with `tracemalloc`.
  - Monitors CPU usage using `psutil`.
  - Records the start and end time to calculate execution duration.
  - Returns metrics including memory usage, execution time, CPU usage, and status (success/error).

### 2. `test_all_functions(functions)`
- **Description**: Tests all functions provided as input and aggregates performance metrics.
- **Key Steps**:
  - Iterates through each function, executing and logging results.
  - Captures overall status and performance metrics for all functions.

### 3. `run_page_test(page_name, test_mode="individual")`
- **Description**: Runs stress tests for a specific page in either **individual** or **comprehensive** mode.
- **Key Steps**:
  - Looks up the page by name and retrieves its associated functions.
  - Runs tests individually or collectively depending on the mode.

### 4. `stress_test_selected_page(page, num_cores, test_mode)`
- **Description**: Main entry point for running stress tests on a selected page.
- **Key Steps**:
  - Initializes the `PageStressTester`.
  - Executes the `run_page_test` method for the selected page and mode.
  - Captures and returns results, including the number of pages tested and the cores used.

### 5. `display_individual_metrics(metrics)`
- **Description**: Displays metrics for individual function tests in a Streamlit dashboard.
- **Key Steps**:
  - Formats execution time, CPU usage, memory usage, and status using Streamlit components.
  - Displays error messages if present.

### 6. `display_comprehensive_metrics(metrics)`
- **Description**: Displays aggregated metrics for comprehensive tests.
- **Key Steps**:
  - Shows combined metrics such as total execution time and peak memory usage.
  - Lists individual function results with statuses and errors.

### 7. `main()`
- **Description**: Orchestrates the user interface for stress testing using Streamlit.
- **Key Steps**:
  - Configures user input options such as CPU cores, pages, and test modes.
  - Executes the selected stress test and displays results in a user-friendly format.

---

## Page and Function Mapping

The application organizes functions into categories based on pages:

| **Page**            | **Functions**                             |
|---------------------|-------------------------------------------|
| Business Group      | `static_part`, `node_details_input`, `create_graph` |
| Parts               | `static_part`, `node_details_input`, `queries`       |
| Product Family      | `static_part`, `node_details_input`, `create_graph` |
| Product Offering    | `static_part`, `node_details_input`, `queries`       |
| Warehouse           | `static_part`, `node_details_input`, `create_graph` |
| Supplier            | `static_part`, `node_details_input`, `queries`       |

---

## How to Use

1. **Select CPU Cores**:
   - Choose the number of cores to allocate for testing.
2. **Select a Page**:
   - Pick a page to test from the dropdown.
3. **Choose Test Mode**:
   - **Individual**: Test each function separately.
   - **Comprehensive**: Test all functions together.
4. **Run the Test**:
   - Click the "Run Stress Test" button.
5. **View Results**:
   - Examine metrics displayed in the dashboard for detailed insights.

---

## Outputs and Metrics

- **Execution Time**: Total time taken to execute the function.
- **CPU Usage**: Percentage of CPU resources utilized.
- **Memory Usage**:
  - Current memory usage.
  - Peak memory usage during execution.
- **Status**:
  - Success/Error status of the function.
  - Error messages if applicable.

---

## Example Usage Scenario

1. Test the "Parts" page in **individual** mode.
2. View detailed metrics for each function on the "Parts" page.
3. Identify functions with high resource usage or errors.
4. Optimize the identified bottlenecks to improve performance.

---

This documentation provides a comprehensive understanding of the stress testing dashboard, its purpose, and how to use it effectively.
