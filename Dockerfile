# ---------- STAGE 1: Builder ----------
FROM python:3.12-slim AS builder

WORKDIR /app

# Install system dependencies including wkhtmltopdf
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libpq-dev \
    curl \
    git \
    && apt-get clean && rm -rf /var/lib/apt/lists/* /var/cache/apt/*

# Install wkhtmltopdf separately with its dependencies
RUN apt-get update && apt-get install -y \
    xfonts-75dpi \
    xfonts-base \
    && wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-2/wkhtmltox_0.12.6.1-2.bullseye_amd64.deb \
    && dpkg -i wkhtmltox_0.12.6.1-2.bullseye_amd64.deb \
    && apt-get install -f \
    && rm wkhtmltox_0.12.6.1-2.bullseye_amd64.deb

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ---------- STAGE 2: Runtime ----------
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libpq5 \
    xfonts-75dpi \
    xfonts-base \
    && rm -rf /var/lib/apt/lists/*

# Install wkhtmltopdf separately
COPY --from=builder /usr/local/bin/wkhtmltopdf /usr/local/bin/
COPY --from=builder /usr/local/bin/wkhtmltoimage /usr/local/bin/
COPY --from=builder /usr/local/lib/libwkhtmltox* /usr/local/lib/

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application code
COPY . .

# Expose the port your app runs on
EXPOSE 8000