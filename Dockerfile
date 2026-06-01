FROM python:3.12-slim

WORKDIR /app

# Install dependencies first so they're cached across code changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code.
COPY app.py get.py index.html ./

EXPOSE 5000

# Serve with gunicorn (binds 0.0.0.0 so the port is reachable from the host).
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "app:app"]
