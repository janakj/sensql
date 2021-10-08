FROM python:3.9

# Allow statements and log messages to immediately appear in the log
ENV PYTHONUNBUFFERED True
ENV PORT 80

RUN mkdir /app
WORKDIR /app

COPY app.py .
COPY requirements.txt .

RUN pip install -r requirements.txt
RUN pip install gunicorn

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app