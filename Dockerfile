FROM python:3.12-alpine

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

COPY ./bot_constructor .
COPY ./requirements.txt .
COPY ./run.sh .

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

RUN chmod +x ./run.sh

CMD ["./run.sh"]