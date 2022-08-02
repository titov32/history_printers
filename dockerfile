FROM python3.8
LABEL maintainer="Evgeniy Titov titov32@gmail.com"
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY ./app /app