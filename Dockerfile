# ---------- STAGE 1: Builder ----------
FROM python:3.12-slim AS builder

WORKDIR /app

# Install system dependencies for WeasyPrint + wkhtmltopdf
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libpq-dev \
    fontconfig \
    libxrender1 \
    wget \
    curl \
    git \
 && wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.bullseye_amd64.deb \
 && apt install -y ./wkhtmltox_0.12.6-1.bullseye_amd64.deb \
 && rm -f wkhtmltox_0.12.6-1.bullseye_amd64.deb \
 && apt-get clean && rm -rf /var/lib/apt/lists/* /var/cache/apt/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# ---------- STAGE 2: Runtime ----------
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Install runtime dependencies for WeasyPrint + wkhtmltopdf
RUN apt-get update && apt-get install -y --no-install-recommends \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    libpq5 \
    fontconfig \
    libxrender1 \
    wget \
 && wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.bullseye_amd64.deb \
 && apt install -y ./wkhtmltox_0.12.6-1.bullseye_amd64.deb \
 && rm -f wkhtmltox_0.12.6-1.bullseye_amd64.deb \
 && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv
COPY . .
