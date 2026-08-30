FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install frontend Python dependencies
COPY frontend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy frontend source code
COPY frontend /app/frontend

ENV PYTHONUNBUFFERED=1
ENV BACKEND_URL=http://backend:8000
ENV PORT=8501

EXPOSE 8501

WORKDIR /app/frontend

CMD ["sh", "-c", "streamlit run app.py --server.port=${PORT:-8501} --server.address=0.0.0.0"]
