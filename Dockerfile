FROM python:3.13-slim

# Don't write .pyc files, and show logs straight away instead of buffering them
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first, so this layer is cached when only the code changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run as a normal user rather than root
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000

# Create any missing tables, then start the API
CMD ["sh", "-c", "python database.py && uvicorn main:app --host 0.0.0.0 --port 8000"]
