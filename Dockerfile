# Use official Python base image
FROM python:3.8

# Set working directory inside container
WORKDIR /

# Copy requirements first (for better caching)
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrandr2 \
    && rm -rf /var/lib/apt/lists/*

# Copy all project files into container
COPY main.py ./main.py
COPY API ./API
COPY app ./app
COPY Effects ./Effects
COPY Logic ./Logic
COPY maps ./maps
COPY Tracking ./Tracking
COPY UI ./UI

# Run your app
CMD ["python", "API/api.py"]
