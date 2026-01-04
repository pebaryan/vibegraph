FROM python:3.12-slim

# Install system dependencies if needed (none usually required for flasgger)
WORKDIR /app

# Copy requirements first to leverage caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code (including swagger.yaml and app.py)
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

EXPOSE 5000
CMD ["python", "app.py"]