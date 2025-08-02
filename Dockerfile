FROM python:3.13-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    && apt-get clean \
    && pip install --no-cache-dir -r requirements.txt \
    && rm -rf /var/lib/apt/lists/*

# Copy the rest of the application
COPY . .

# Create logs directory with proper permissions and create a non-root user
RUN mkdir -p /app/logs && chmod 777 /app/logs && useradd -m appuser
USER appuser

# Run the application
CMD ["python", "src/main.py"]