FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create logs directory with proper permissions and create a non-root user
RUN mkdir -p /app/logs && chmod 777 /app/logs && useradd -m appuser
USER appuser

# Run the application
CMD ["python", "src/main.py"]