FROM python:3.12-alpine

WORKDIR /app

COPY ./bot_constructor .
COPY ./requirements.txt .
COPY ./run.sh .

RUN pip install -r requirements.txt

ENV PYTHONUNBUFFERED=1

CMD ["sh", "run.sh"]