# Main Application
# To be replaced by subiksha akka

## Overview

The Main Application (`Main.py`) serves as the entry point for the Supply Chain Dashboard. It initializes the dashboard application and handles the core functionality.

## Key Components

### Dashboard Initialization
- Sets up the web server
- Initializes the temporal graph
- Configures the visualization components

### Data Processing
- Loads supply chain data
- Processes temporal relationships
- Updates graph visualizations

### API Integration
- Exposes REST endpoints for data access
- Handles real-time updates
- Manages data synchronization

## Configuration

The main application can be configured through:
- Environment variables (`.env` file)
- Command line arguments
- Configuration file (`config.py`)

## Usage

To run the application:
```bash
streamlit run Main.py
```

For development mode:
```bash
streamlit run Main.py --debug
```
