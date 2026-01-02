FROM python:3.10-slim

# Install system dependencies
# ffmpeg is often needed for video processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first to leverage cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ src/
COPY .env .

# Create downloads directory
RUN mkdir -p downloads

# Run the bot
CMD ["python", "src/main.py"]
