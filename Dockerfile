FROM python:3.11-slim

# Install xvfb for headless Chrome support
RUN apt-get update && apt-get install -y \
    xvfb \
    libxkbcommon0 \
    libdrm2 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY web_app.py .
COPY templates/ ./templates/

EXPOSE 5000

CMD ["python", "web_app.py"]
