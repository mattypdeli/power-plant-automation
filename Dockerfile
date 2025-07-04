# Step 1: Choose our base container.
FROM python:3.11-slim

# Step 2: Set a "workshop" directory inside the container.
WORKDIR /app

# Step 3: Copy ONLY the requirements file first.
COPY requirements.txt .

# Step 4: Install the libraries from our "shopping list".
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Now, copy all of our application code into the workshop.
COPY . .

# Step 6: Define the default command to run when the container starts.
# THIS IS THE CORRECTED LINE:
CMD ["bentoml", "serve", "app:svc", "--production"]