# Smart AI Legal Automation Platform - Production Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    HOST=0.0.0.0 \
    CHROME_BIN=/usr/bin/chromium

# Install system dependencies for headless Chromium/PDF and font rendering
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    fonts-beng \
    fonts-lohit-beng-bengali \
    fonts-freefont-ttf \
    fonts-noto-cjk \
    fonts-sil-padauk \
    curl \
    fontconfig \
    && mkdir -p /usr/share/fonts/truetype/hind-siliguri \
    && curl -sL "https://github.com/google/fonts/raw/main/ofl/hindsiliguri/HindSiliguri-Regular.ttf" -o /usr/share/fonts/truetype/hind-siliguri/HindSiliguri-Regular.ttf || true \
    && curl -sL "https://github.com/google/fonts/raw/main/ofl/hindsiliguri/HindSiliguri-Bold.ttf" -o /usr/share/fonts/truetype/hind-siliguri/HindSiliguri-Bold.ttf || true \
    && fc-cache -f \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency specifications and install
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY backend /app/backend

# Copy frontend static code
COPY frontend /app/frontend

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Launch production uvicorn server
WORKDIR /app/backend
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
