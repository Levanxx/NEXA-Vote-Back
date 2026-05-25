FROM python:3.11

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 10000

CMD sh -c "gunicorn -w 4 -b 0.0.0.0:${PORT:-10000} app:app"