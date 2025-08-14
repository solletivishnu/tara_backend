# ---------- STAGE 1: Builder ----------
FROM python:3.12-slim AS builder

WORKDIR /app

# Install system dependencies for WeasyPrint (no wkhtmltopdf here)
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libpq-dev \
    curl \
    git \
    && apt-get clean && rm -rf /var/lib/apt/lists/* /var/cache/apt/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Download portable wkhtmltopdf (static binary)
RUN curl -L https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox-0.12.6-1.tar.xz \
    -o wkhtmltox.tar.xz \
    && mkdir -p /opt/wkhtmltopdf \
    && tar -xJf wkhtmltox.tar.xz -C /opt/wkhtmltopdf --strip-components=1 \
    && rm wkhtmltox.tar.xz

# ---------- STAGE 2: Runtime ----------
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:/opt/wkhtmltopdf/bin:$PATH"

WORKDIR /app

# Install runtime dependencies for WeasyPrint
RUN apt-get update && apt-get install -y --no-install-recommends \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    libpq5 \
    fontconfig \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

# Copy venv and wkhtmltopdf from builder
COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /opt/wkhtmltopdf /opt/wkhtmltopdf

# Copy app
COPY . .

# CMD ["uvicorn", "Tara.asgi:application", "--host", "0.0.0.0", "--port", "8000"]
