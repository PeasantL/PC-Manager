FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create a non-root user for security
RUN useradd -m appuser
USER appuser

# Environment variables
ENV DEV_MODE=false

# Expose the port
EXPOSE 808

# Command to run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "808"]
