FROM python:3.10-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir mkdocs mkdocs-material

# Copy the rest of the application
COPY . .

# Build documentation
RUN python -m mkdocs build

EXPOSE 8000

CMD ["python", "Main.py"]
