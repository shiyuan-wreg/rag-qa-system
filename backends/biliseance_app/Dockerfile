FROM python:3.12-slim

WORKDIR /app

COPY backends/biliseance_app/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backends/biliseance_app/ ./

EXPOSE 8006

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8006"]
