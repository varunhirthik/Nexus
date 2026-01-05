FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY data/ ./data/
COPY .env.example ./.env.example

# Create necessary directories
RUN mkdir -p data/output data/breaking_news

# Expose Pathway port
EXPOSE 8000

# Environment variables (override with docker-compose)
ENV PYTHONUNBUFFERED=1
ENV PATHWAY_HOST=0.0.0.0
ENV PATHWAY_PORT=8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the pipeline
CMD ["python", "-u", "src/main.py"]
