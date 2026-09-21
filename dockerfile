FROM apache/airflow:2.9.1-python3.10

COPY requirements.txt /requirements.txt

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r /requirements.txt