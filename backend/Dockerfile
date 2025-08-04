FROM python:3.9

WORKDIR /app

RUN pip install gunicorn==20.1.0

COPY requirements.txt .

RUN pip install -r requirements.txt

RUN python -m pip install --upgrade pip

COPY . .

CMD ["sh", "entrypoint.sh"]