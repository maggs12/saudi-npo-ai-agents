FROM python:3.10-slim

WORKDIR /app

# Install system fonts for Arabic PDF generation and clean apt cache
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        fonts-noto-core \
        fontconfig && \
    rm -rf /var/lib/apt/lists/* && \
    fc-cache -fv

# Install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy application code
COPY backend/ /app/

# Ensure reports directory exists
RUN mkdir -p /app/reports

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
