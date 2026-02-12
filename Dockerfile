# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies based on requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code into the container
COPY src ./src

# Create a non-root user and switch to it
RUN useradd -m appuser
USER appuser

# Run the application
ENTRYPOINT ["python", "src/main.py"]
CMD ["--help"]
