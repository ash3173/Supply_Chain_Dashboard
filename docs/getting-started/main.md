# Main Application Documentation

## Overview
The Main Application serves as the core entry point for the Supply Chain Dashboard, implementing a temporal graph-based system for supply chain analysis and visualization.

## Configuration

### API Endpoints
```python
base_url = "sample_base_url"
version = "sample_version"
```

### Available Endpoints
- **Versions**: `{base_url}/versions`
- **Schema Timestamp**: `{base_url}/archive/schema/{version}`
- **Data Retrieval**: `{base_url}/archive/schema/{version}`
- **Live Data**: `{base_url}/live/schema/{version}`

## Data Management

### Local Storage
- **Data Directory**: `data/`
- **Version-specific Storage**: `data/{version}/`
- **File Format**: JSON files named by timestamps

### Data Synchronization Process
1. **Version Verification**
    - Checks if version exists locally
    - Validates version against server
    - Creates version directory if needed

2. **Timestamp Management**
    - Retrieves all timestamps from server
    - Compares with local files
    - Downloads missing timestamp data

3. **File Organization**
    - Sorts files by timestamp
    - Maintains chronological order
    - Ensures data consistency

## Temporal Graph Implementation

### Initialization
```python
temporal_graph = TemporalGraphClass(all_files)
```

### Features
- Processes multiple JSON files
- Maintains temporal relationships
- Stores graph state in session

## Application Flow

1. **Startup**
    - Directory verification
    - Version validation

2. **Data Processing**
    - Server data retrieval
    - Local file management
    - Temporal graph initialization

3. **State Management**
    - Session state initialization
    - Graph state persistence
    - Success confirmation

## Error Handling
- Directory existence checks
- Server version validation
- API response validation
- File system management

## Usage

### Running the Application
```bash
streamlit run main.py
```

### Data Structure
```
data/
└── sample_version/
    ├── timestamp1.json
    ├── timestamp2.json
    └── ...
```

## Dependencies
- Streamlit: Web interface
- Requests: API communication
- JSON: Data formatting
- OS: File system operations

## Best Practices
1. Regular data synchronization
2. Version control monitoring
3. File system organization
4. Session state management

## Future Enhancements
1. Additional version support
2. Enhanced error handling
3. Improved data validation
4. Extended API functionality