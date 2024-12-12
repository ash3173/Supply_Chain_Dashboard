# Supply Chain Dashboard

## Overview
The Supply Chain Dashboard is a comprehensive web application built with Streamlit that provides real-time insights into supply chain operations. The dashboard offers multiple views and analyses for different components of the supply chain network.

## Key Components

### 1. Data Management
- Version control for supply chain schemas
- Timestamp-based data retrieval
- Real-time and archived data access

### 2. Interactive Visualizations
- Network graphs showing supply chain relationships
- Time series analysis of various metrics
- Interactive filters and selectors

### 3. Entity Analysis
- [Business Group](business_group.md): Revenue analysis and group relationships
- [Product Family](product_family.md): Product categorization and performance
- [Product Offering](product_offering.md): Individual product details and metrics
- [Warehouse](warehouse.md): Inventory management and distribution
- [Facility](facility.md): Manufacturing and production insights
- [Parts](parts.md): Component tracking and inventory
- [Supplier](supplier.md): Supplier relationships and performance

## Technical Architecture

### Backend Components
- Graph database for relationship management
- REST APIs for data retrieval
- Caching mechanisms for performance optimization

### Frontend Features
- Responsive Streamlit interface
- Interactive plotly visualizations
- NetworkX-based graph visualizations

## Performance Features
- Memory usage tracking
- Execution time monitoring
- Caching for frequently accessed data

## Usage Instructions
1. Select the desired view from the sidebar
2. Choose the relevant time period using the timestamp selector
3. Use filters to focus on specific entities or relationships
4. Interact with visualizations for detailed insights
5. Export or share analysis results as needed

## Dependencies
- Streamlit: Web application framework
- NetworkX: Graph operations and analysis
- Plotly: Interactive visualizations
- Matplotlib: Static visualizations
- Python-dotenv: Environment configuration
- Requests: API communication

## Best Practices
- Regular data synchronization
- Cache clearing for memory management
- Proper error handling
- Performance monitoring

## Future Enhancements
- Advanced analytics integration
- Machine learning predictions
- Additional visualization options
- Enhanced export capabilities
- Real-time alerts and notifications