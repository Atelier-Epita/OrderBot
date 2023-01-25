FROM python:3.9

WORKDIR /app

COPY ./setup.py /app/setup.py

RUN pip install -e .

COPY . /app

CMD ["python3", "-m", "orderbot"]