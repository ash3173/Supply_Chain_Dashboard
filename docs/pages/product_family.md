# Product Family Page

## Overview

The Product Family page (`2_Product_Family.py`) manages product families and their relationships within the supply chain ecosystem.

## Features

### Product Family Management
- Create and maintain product families
- Define product hierarchies
- Track product relationships

### Analysis Tools
- Product family comparison
- Market segment analysis
- Performance tracking

### Data Visualization
- Product family tree view
- Relationship graphs
- Performance dashboards

## Usage

The Product Family page provides tools for:
- Creating new product families
- Managing product hierarchies
- Analyzing product relationships
- Generating product reports
- Tracking product metrics

## Integration

The page integrates with:
- Business Group data
- Product Offering information
- Supply chain metrics

## Product Family Dashboard

### Key Features

#### 1. Finding Product Families with Highest Revenue
- Automated tracking of top-performing product families
- Revenue comparison across different time periods
- Visual representation of revenue distribution

#### 2. Revenue Trends
- Time-series analysis of product family performance
- Comparative revenue analysis
- Trend identification and visualization

#### 3. Revenue Visualization
- Interactive line charts showing revenue progression
- Time-series representation of revenue changes
- Shaded area under the line for visual emphasis

#### 4. Product Family Details
- Detailed information display for selected product families
- Key metrics including:
  - Name
  - Description
  - Revenue
  - ID
  - Associated Business Groups

### Overview
The Product Family Dashboard provides insights into product category performance and relationships within the supply chain network. This tool helps analyze revenue patterns, product hierarchies, and business group associations.

### Data Exploration and Visualization

#### **1. Product Family Schema**
- Hierarchical visualization of product families and their relationships
- Connection mapping to business groups and product offerings
- Attributes displayed:
  - Product Family: Node type, name, revenue, ID
  - Related Entities: Business groups, product offerings

#### **2. Revenue Analysis**
- Dynamic visualization of revenue trends
- Comparative analysis across product families
- Features:
  - Multi-panel revenue plots
  - Time-based performance tracking
  - Revenue distribution patterns

#### **3. Top Product Families**
- Identification of highest-performing product families
- Revenue-based ranking system
- Visual representation of top performers

#### **4. Relationship Analysis**
- Business group associations
- Product offering connections
- Network visualization of product family relationships

### Code Structure

#### **1. Utility Functions**
- Performance tracking decorators
- Graph creation and manipulation
- Revenue calculation and analysis
- Visualization helpers

#### **2. Streamlit Components**
- Interactive filters and selectors
- Dynamic visualizations
- Data presentation layouts

#### **3. Main Function**
- Dashboard initialization
- Component organization
- User interaction handling

### Usage Instructions
1. Select time range using timestamp slider
2. Choose specific product families for analysis
3. View revenue trends and relationships
4. Explore detailed product family information

### Performance Considerations
- Optimized data retrieval
- Efficient memory management
- Response time monitoring

### Dependencies
- Streamlit: Dashboard framework
- NetworkX: Graph operations
- Plotly: Interactive visualizations
- Matplotlib: Static charts
- Tracemalloc: Performance monitoring

### Recommended Improvements
- Enhanced filtering capabilities
- Additional performance metrics
- Advanced trend analysis
- Predictive analytics integration
