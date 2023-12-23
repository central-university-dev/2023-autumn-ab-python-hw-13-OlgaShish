# Use an official Python runtime as a parent image
FROM python:3.11 AS builder

# Set work directory
WORKDIR /opt/build

# Install Poetry
RUN pip install poetry
RUN pip install flake8-bandit

# Copy only requirements to cache them in docker layer
COPY pyproject.toml poetry.lock hw_15 config.json .bandit ./

# Project initialization:
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev

# Start final image
FROM python:3.11-slim

WORKDIR /opt/app

# Copy only the relevant files from the builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY ./ config.json /opt/app/

# Application entrypoint
CMD ["uvicorn", "hw_15.main:application", "--host", "0.0.0.0", "--port", "8000"]
