FROM python:3.9
LABEL maintainer="Evgeniy Titov titov32@gmail.com"
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --upgrade pip && pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./app /code/app
WORKDIR /code/app
CMD ['python', 'init_db.py']
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
WORKDIR /code/app/alembic
CMD ['alembic upgrade head']
ENV POSTGRESUSER='USER_DATABASE'
ENV POSTGRESPASS='PASSWORD_DATABASE'
ENV POSTGRESDB='prn'

