FROM python:3.12-slim
WORKDIR /app
COPY backends/nexus_app/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY core/ ./core/
COPY backends/nexus_app/ ./backends/nexus_app/
EXPOSE 8003
CMD ["uvicorn", "backends.nexus_app.main:app", "--host", "0.0.0.0", "--port", "8003"]
