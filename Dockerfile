FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 10000

CMD sh -c "gunicorn -w 1 --timeout 120 -b 0.0.0.0:${PORT:-10000} 'run:app'"