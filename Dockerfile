# Use official Python slim image
FROM python:3.12-slim

# Set working directory in the container
WORKDIR /app

# Copy dependency file first (better layer caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .

# Expose port (uvicorn default)
EXPOSE 8000

# Run the app with uvicorn (host 0.0.0.0 so Docker can forward ports)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
