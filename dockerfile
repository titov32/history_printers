FROM python:3.9
LABEL maintainer="Evgeniy Titov titov32@gmail.com"
RUN groupadd -r prn && useradd -s /bin/bash -d /home/prn -m -r -g prn prn
WORKDIR /code
RUN python -m venv /code/venv
ENV PATH="/code/venv/bin:$PATH"
COPY ./requirements.txt /code/requirements.txt
COPY ./app /code/app
WORKDIR /code/app
RUN chown -R prn:prn /code 
USER prn
ENV POSTGRESUSER='prn'
ENV POSTGRESPASS='password'
ENV POSTGRESDB='prn'
#настройки прокси
#ENV http_proxy="http://login:password@host:port" 
#ENV https_proxy="http://login:password@host:port" 
RUN ../venv/bin/pip install --upgrade pip
RUN pip3 install -r /code/requirements.txt
RUN python init_db.py
