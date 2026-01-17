# 1. Use Python 3.11 (Matches your Mac version to prevent dependency errors)
FROM python:3.11-slim

# 2. Force Python to print logs immediately (Helps us debug if it crashes)
ENV PYTHONUNBUFFERED=1

# 3. Set the working directory inside the container
WORKDIR /app

# 4. Copy requirements file first
COPY requirements.txt .

# 5. Install dependencies
# Added default-timeout to prevent "ReadTimeoutError" on slow connections
RUN pip install --default-timeout=1000 --no-cache-dir -r requirements.txt

# 6. Copy the rest of your code
COPY . .

# 7. Run the seed script to "bake" the AI models into the image
RUN python seed_references.py

# 8. Start the app (The Critical Fix)
# We use "sh -c" so we can read the ${PORT} variable from Render.
# If Render gives a port (usually 10000), we use it. If not, we use 8000.
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}"]