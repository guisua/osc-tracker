# syntax=docker/dockerfile:1

FROM python:3.13-slim

# Set environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install uv
RUN pip install uv

# Create app directory
WORKDIR /app

# Copy pyproject.toml and optionally uv.lock
COPY pyproject.toml ./

# Install dependencies
RUN uv pip install --system .

# Copy app code
COPY app/ app/
COPY main.py .

# Expose port
EXPOSE 8000
EXPOSE 9000

# Start app (adjust import path as needed)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
