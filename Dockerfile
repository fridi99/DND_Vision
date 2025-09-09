# Use official Python base image
FROM python:3.9

ENV PYTHONUNBUFFERED=1


# Set working directory inside container
WORKDIR /app

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

COPY . .


# Run your app
CMD ["python", "-m" , "API.api"]
