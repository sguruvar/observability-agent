FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY ai-agent/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ai-agent/ .

# Create templates directory
RUN mkdir -p templates

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "app.py"]
