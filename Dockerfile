# Use an official lightweight Python image
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable buffered stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install minimal system dependencies needed for some Python packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker layer caching
COPY requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements.txt

# Copy application source
COPY . /app

# Create a non-root user and give ownership of the app directory
RUN useradd --create-home appuser \
    && chown -R appuser:appuser /app
USER appuser

# Expose the Gradio port used by the app
EXPOSE 7860

ENV PORT=7860

# Simple healthcheck (requires curl installed in image; included above)
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:7860/ || exit 1

# Run the app
CMD ["python", "app.py"]
