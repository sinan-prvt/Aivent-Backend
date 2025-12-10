FROM python:3.11-slim
WORKDIR /usr/src/app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .
RUN apt-get update && apt-get install -y netcat-openbsd gcc libpq-dev && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r requirements.txt --default-timeout=200 -i https://pypi.org/simple


COPY . .

COPY ./wait-for-db.sh /wait-for-db.sh
RUN chmod +x /wait-for-db.sh

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "vendor_project.wsgi:application"]
