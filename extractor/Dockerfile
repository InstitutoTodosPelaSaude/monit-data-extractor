FROM python:3.11-slim

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

CMD ["python", "download_files.py"]