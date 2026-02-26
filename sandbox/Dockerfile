FROM python:3.9-slim

# Install Chromium and dependencies
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy runner script
COPY runner.py .

# Create output directory
RUN mkdir /out

ENTRYPOINT ["python", "runner.py"]
