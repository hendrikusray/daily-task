FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app/ ./app

# Set environment
ENV PYTHONUNBUFFERED=1
ENV PRODUCTION=1

# Expose port
EXPOSE 7860

# Run with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--workers", "2", "--chdir", "app", "app:app"]
