FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements for shared packages if needed, then install streamlit requirements
COPY backend/requirements.txt /app/backend_reqs.txt
RUN pip install --no-cache-dir -r backend_reqs.txt
RUN pip install --no-cache-dir streamlit plotly pandas

# Copy frontend source code
COPY frontend /app/frontend

ENV PYTHONUNBUFFERED=1
ENV BACKEND_URL=http://backend:8000

EXPOSE 8501

WORKDIR /app/frontend

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
