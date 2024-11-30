# Use the official Python image from the Docker Hub
FROM python:3.12-slim

# Install system dependencies for building aiohttp and other packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libssl-dev \
    libffi-dev \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire app into the container
COPY . .

# Command to run the application
CMD ["python", "main.py"]
