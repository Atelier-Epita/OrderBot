FROM python:3.9

WORKDIR /app

COPY ./setup.py /app/setup.py
COPY ./orderbot/ /app/orderbot/

RUN pip install -e .

COPY . /app

CMD ["python3", "-m", "orderbot"]