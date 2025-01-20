FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

RUN python manage.py makemigrations && python manage.py migrate

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

