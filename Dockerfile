# Use Python 3.10 as the base image (change to match your required version)
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies and Poetry
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    curl \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && rm -rf /var/lib/apt/lists/*

# Add Poetry to PATH
ENV PATH="/root/.local/bin:$PATH"

# Copy pyproject.toml and poetry.lock
COPY pyproject.toml poetry.lock /app/

# Use the Python version available in the container with Poetry
RUN poetry env use /usr/local/bin/python3

# Install Python dependencies using Poetry
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi

# Copy the project files into the container
COPY . /app/

# Copy the entrypoint script into the container
COPY entrypoint.sh /app/entrypoint.sh

# Ensure the entrypoint script is executable
RUN chmod +x /app/entrypoint.sh

# Verify that the script has the correct permissions
RUN ls -l /app/entrypoint.sh

# Use the entrypoint script to run the Django app
ENTRYPOINT ["/app/entrypoint.sh"]
