# Installation Guide

## Prerequisites

- Python 3.8 or higher
- pip package manager
- Docker (optional, for containerized deployment)

## Installation Steps

1. Clone the repository:
```bash
git clone <repository-url>
cd Supply_Chain_Dashboard
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure the environment:
```bash
cp .env.default .env
# Edit .env with your configuration
```

## Docker Installation

To run using Docker:

1. Build the Docker image:
```bash
docker-compose build
```

2. Run the container:
```bash
docker-compose up
```

## Verification

To verify the installation:

1. Run the application:
```bash
streamlit run Main.py
```

2. Open a web browser and navigate to the application URL (default: http://localhost:8000)
