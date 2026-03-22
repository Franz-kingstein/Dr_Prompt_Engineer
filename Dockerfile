# ============================================================
# Stage 1: Build React frontend
# ============================================================
FROM node:20-slim AS frontend-builder

WORKDIR /frontend

# Copy frontend package files first (cache layer)
COPY frontend/package*.json ./
RUN npm ci

# Copy frontend source and build
COPY frontend/ ./
RUN npm run build

# ============================================================
# Stage 2: Python backend (production)
# ============================================================
FROM python:3.12-slim AS backend

WORKDIR /app

# Install only the OS-level dependencies we need
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Use the trimmed requirements file (no CUDA/torch/vLLM bloat)
COPY requirements-deploy.txt .
RUN pip install --no-cache-dir -r requirements-deploy.txt

# Copy application source
COPY . .

# Copy built frontend into the expected static location
# FastAPI will serve this via StaticFiles mount
COPY --from=frontend-builder /frontend/dist ./frontend/dist

# Render (and most cloud platforms) inject PORT at runtime.
# We default to 8000 for local runs.
ENV PORT=8000
ENV PYTHONUNBUFFERED=1

# Expose (documentation only – Render reads $PORT dynamically)
EXPOSE ${PORT}

# Use shell-form CMD so $PORT is expanded at container start time
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT}
