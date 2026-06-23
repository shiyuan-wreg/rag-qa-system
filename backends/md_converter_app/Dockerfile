FROM python:3.12-slim

WORKDIR /app

COPY backends/md_converter_app/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backends/md_converter_app/ ./

EXPOSE 8004

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8004"]
