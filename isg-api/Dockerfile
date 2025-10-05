FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (avoid deprecated libgl1-mesa-glx, use libgl1) and reduce layer size
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    gcc \
    curl \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create static directory structure with proper permissions before switching to non-root user
RUN mkdir -p /app/static/employees && chown -R app:app /app

# Create non-root user
RUN useradd --create-home --shell /bin/bash app || true
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -fsS http://localhost:8000/health || exit 1

# Default command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]