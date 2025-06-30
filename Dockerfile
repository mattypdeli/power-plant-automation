# Step 1: Choose our base container.
# We're starting with a lightweight, official Python environment.
FROM python:3.11-slim

# Step 2: Set a "workshop" directory inside the container.
# All our work will happen inside this '/app' folder.
WORKDIR /app

# Step 3: Copy ONLY the requirements file first.
# This is an efficiency trick. Docker caches steps, and since our
# libraries change less often than our code, this layer won't
# need to be rebuilt as often.
COPY requirements.txt .

# Step 4: Install the libraries from our "shopping list".
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Now, copy all of our application code into the workshop.
# This includes our app.py file.
COPY . .

# Step 6: Define the default command to run when the container starts.
# This tells the container to execute our python script.
CMD ["python", "app.py"]