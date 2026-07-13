FROM python:3.12-alpine

WORKDIR /app

COPY ./bot_constructor .
COPY ./requirements.txt .
COPY ./run.sh .

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

ENV PYTHONUNBUFFERED=1

RUN chmod +x ./run.sh

CMD ["./run.sh"]