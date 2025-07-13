# Stage 1: Builder - Install tools, build the Bento artifact
FROM python:3.12-slim AS builder

# Set working directory
WORKDIR /builder

# Install system dependencies for building (optional but safe for Python deps)
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

# Copy and install requirements for the build process (needed to import during bentoml build)
COPY requirements.txt /builder/
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir bentoml

# Copy the application files
COPY app.py /builder/
COPY bentofile.yaml /builder/
COPY erp_database.db /builder/

# Build the Bento (this runs bentoml build .)
RUN bentoml build .

# Stage 2: Runtime - Minimal image to serve the Bento
FROM python:3.12-slim

# Install bentoml for the serve command (no other deps needed, as bento is self-contained)
RUN pip install --no-cache-dir bentoml && \
    # Create non-root user for security
    adduser --disabled-password --gecos '' bentoml

# Copy the entire Bento artifact directory from builder (includes latest symlink and version dir)
COPY --from=builder --chown=bentoml:bentoml /root/.bentoml/bentos/power_plant_rag_service /home/bentoml/.bentoml/bentos/power_plant_rag_service

# Set working directory (arbitrary, since we serve by tag)
WORKDIR /home/bentoml

# Switch to non-root user
USER bentoml

# Expose the BentoML port
EXPOSE 3000

# Run the service in production mode
CMD ["bentoml", "serve", "power_plant_rag_service:latest", "--production"]