# ==================================
# Stage 1: Build Frontend
# ==================================
FROM node:24 AS frontend-build

WORKDIR /app-frontend

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./
ARG VITE_API_URL=/api/v1
RUN npm run build


# ==================================
# Stage 2: Build Backend Environment
# ==================================
FROM python:3.10 AS backend-build

WORKDIR /app

# Install uv for fast package management
COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /uvx /bin/

ENV PYTHONUNBUFFERED=1
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Copy dependency files
COPY backend/pyproject.toml backend/uv.lock backend/alembic.ini ./

# Install dependencies into virtualenv
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project


# ==================================
# Stage 3: Final Runtime Image
# ==================================
FROM python:3.10-slim

WORKDIR /app

# Install Nginx and Supervisor
RUN apt-get update && apt-get install -y \
    nginx \
    supervisor \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Backend Virtual Environment from backend-build
COPY --from=backend-build /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy Backend Code
COPY backend/scripts /app/scripts
COPY backend/pyproject.toml backend/uv.lock backend/alembic.ini /app/
COPY backend/app /app/app

# Copy Frontend Build Artifacts
COPY --from=frontend-build /app-frontend/dist /usr/share/nginx/html

# Copy Configuration Files
COPY nginx-custom.conf /etc/nginx/conf.d/default.conf
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose Port 80
EXPOSE 80

# Run Supervisor
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
