# syntax=docker/dockerfile:1
FROM python:3.10-alpine3.14
WORKDIR /campaignfinance
COPY ./requirements.txt /campaignfinance
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY . /campaignfinance
CMD ["python", "main", "--host", "0.0.0.0", "--port", "80"]