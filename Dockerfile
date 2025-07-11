# Step 1: Choose our base container.
FROM python:3.11-slim

# Step 2: Install critical system packages
# - ca-certificates: Solves SSL/TLS issues by providing trusted root certificates.
# - dnsutils: Provides the 'dig' command for DNS diagnostics.
# - curl: Provides the 'curl' command for network diagnostics.
RUN apt-get update && apt-get install -y ca-certificates dnsutils curl && rm -rf /var/lib/apt/lists/*

# Step 3: Set a "workshop" directory inside the container.
WORKDIR /app

# Step 4: Copy ONLY the requirements file first.
COPY requirements.txt .

# Step 5: Install the libraries from our "shopping list".
RUN pip install --no-cache-dir -r requirements.txt

# Step 6: Now, copy all of our application code into the workshop.
COPY . .

# Step 7: Define the default command to run when the container starts.
CMD ["bentoml", "serve", "app:MySimpleService", "--production"]