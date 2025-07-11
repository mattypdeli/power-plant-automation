# --- STAGE 1: The Builder ---
FROM python:3.11-slim AS builder
WORKDIR /app
COPY bentofile.yaml .
COPY requirements.txt .
RUN pip install bentoml==1.4.17
RUN pip install -r requirements.txt
COPY app.py .
COPY setup_database.py .
RUN python setup_database.py
RUN --mount=type=secret,id=openai_api_key \
    OPENAI_API_KEY=$(cat /run/secrets/openai_api_key) bentoml build

# --- STAGE 2: The Final Production Image ---
FROM python:3.11-slim
RUN apt-get update && apt-get install -y ca-certificates && rm -rf /var/lib/apt/lists/*
RUN pip install bentoml==1.4.17

# vvv --- THIS IS THE CORRECTED LINE --- vvv
# The trailing slash ensures Docker creates a directory.
COPY --from=builder /root/bentoml/bentos/power_plant_rag_service/latest /home/bentoml/bento/

# Set up a non-root user for security best practices
RUN useradd -m -U -s /bin/false bentoml && chown -R bentoml:bentoml /home/bentoml
USER bentoml
ENV BENTOML_HOME=/home/bentoml

# Set the working directory to the Bento's location
WORKDIR /home/bentoml/bento

# Expose the port
EXPOSE 3000

# The command to run the BentoML server
CMD ["bentoml", "serve", "src.app:PowerPlantRAGService"]