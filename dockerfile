FROM python:3.10.0-alpine

WORKDIR /clip-of-the-day
COPY . .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 8000
CMD [ "gunicorn", "--bind", "0.0.0.0:8000", "--workers", "5", "--timeout", "60", "app:app"]