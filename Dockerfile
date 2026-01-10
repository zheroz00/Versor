FROM debian:bookworm-slim

# Install Python, ImageMagick, Potrace, and build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    imagemagick \
    potrace \
    curl \
    ca-certificates \
    # Build dependencies for autotrace
    build-essential \
    autoconf \
    automake \
    libtool \
    intltool \
    autopoint \
    pkg-config \
    libpng-dev \
    libmagickcore-dev \
    pstoedit \
    libpstoedit-dev \
    && rm -rf /var/lib/apt/lists/*

# Build and install autotrace from source
RUN curl -L https://github.com/autotrace/autotrace/archive/refs/tags/0.31.10.tar.gz \
    -o /tmp/autotrace.tar.gz \
    && cd /tmp \
    && tar xzf autotrace.tar.gz \
    && cd autotrace-0.31.10 \
    && ./autogen.sh \
    && ./configure --prefix=/usr \
    && make \
    && make install \
    && ldconfig \
    && cd / \
    && rm -rf /tmp/autotrace*

# Install vtracer from pre-built binary
RUN curl -L https://github.com/visioncortex/vtracer/releases/download/0.6.4/vtracer-x86_64-unknown-linux-musl.tar.gz \
    -o /tmp/vtracer.tar.gz \
    && tar xzf /tmp/vtracer.tar.gz -C /usr/local/bin \
    && chmod +x /usr/local/bin/vtracer \
    && rm /tmp/vtracer.tar.gz

# Set working directory
WORKDIR /app

# Create virtual environment and install Flask
COPY requirements.txt .
RUN python3 -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .
COPY config.py .
COPY presets.py .
COPY converters/ converters/
COPY templates/ templates/
COPY static/ static/

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH"
ENV POTRACE_PATH=/usr/bin/potrace
ENV AUTOTRACE_PATH=/usr/bin/autotrace
ENV VTRACER_PATH=/usr/local/bin/vtracer
ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 5000

# Run the application
CMD ["python3", "app.py"]
