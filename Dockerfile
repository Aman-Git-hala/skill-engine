# 1. Use a lightweight Python base image
FROM python:3.11-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy requirements first (to cache dependencies)
COPY requirements.txt .

# 4. Install dependencies
# We add --no-cache-dir to keep the image small
RUN pip install --default-timeout=1000 --no-cache-dir -r requirements.txt

# 5. Copy the rest of your code
COPY . .

# 6. RUN THE SEED SCRIPT (Crucial Step)
# This generates the reference_embeddings/*.pkl files INSIDE the image.
# So when you ship this, the "Brain" is already pre-loaded.
RUN python seed_references.py

# 7. Expose the port the app runs on
EXPOSE 8000

# 8. Command to run the app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]