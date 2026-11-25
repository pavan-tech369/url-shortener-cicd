# 1. Start from an official lightweight Python Linux image
FROM python:3.12-slim

# 2. Set the working folder inside the container
WORKDIR /app

# 3. Copy requirements first (Docker caches this layer so rebuilds are fast!)
COPY requirements.txt .

# 4. Install Python dependencies inside the container
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of our application code into /app
COPY app.py .

# 6. Document that our Flask app listens on port 5000
EXPOSE 5000

# 7. Command that runs when the container starts
CMD ["python", "app.py"]