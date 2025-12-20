FROM python:3.11

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Flake8 for linting
RUN pip install flake8

# Install pytest for running unit test
RUN pip install pytest

# Install debugpy for debugging
RUN pip install debugpy

# Install Node.js 18.x and npm
RUN apt-get update \
    && apt-get install -y curl ca-certificates gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Claude Code CLI globally
RUN npm install -g @anthropic-ai/claude-code

# Expose the debug port
EXPOSE 5678

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=development

# Start the app in development mode
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]