# --- STAGE 1: The Builder ---
# This stage installs dependencies and builds the Bento artifact.
FROM python:3.11-slim AS builder

WORKDIR /app

# Copy configuration and requirements files first
COPY bentofile.yaml .
COPY requirements.txt .

# Install bentoml and all other dependencies from requirements.txt
RUN pip install bentoml==1.4.17
RUN pip install -r requirements.txt
    
# Copy the rest of the source files
COPY app.py .
COPY setup_database.py .

# Run the setup script to create the database inside the container
RUN python setup_database.py

# This command securely mounts the secret from the .env file
# and exports it as an environment variable ONLY for the bentoml build command.
RUN --mount=type=secret,id=openai_api_key \
    export OPENAI_API_KEY=$(cat /run/secrets/openai_api_key) && \
    bentoml build

# --- STAGE 2: The Final Production Image ---
# This stage starts from a clean slate and copies ONLY the built Bento.
FROM python:3.11-slim

# Install the critical ca-certificates package for SSL/TLS connections
RUN apt-get update && apt-get install -y ca-certificates && rm -rf /var/lib/apt/lists/*

# vvv --- THIS IS THE CORRECTED LINE --- vvv
# The name must be lowercase with underscores to match what 'bentoml build' creates.
COPY --from=builder /root/bentoml/bentos/power_plant_rag_service/latest /home/bentoml/bento

# Set up a non-root user for security best practices
RUN useradd -m -U -s /bin/false bentoml && chown -R bentoml:bentoml /home/bentoml
USER bentoml
ENV BENTOML_HOME=/home/bentoml

# Expose the port
EXPOSE 3000

# The command to run the BentoML server
CMD ["bentoml", "serve", "/home/bentoml/bento"]