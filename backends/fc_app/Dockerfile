FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backends/fc_app/ ./backends/fc_app/
CMD ["uvicorn", "backends.fc_app.main:app", "--host", "0.0.0.0", "--port", "8002", "--workers", "1"]
