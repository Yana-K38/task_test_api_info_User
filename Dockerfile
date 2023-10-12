FROM python:3.10

RUN mkdir /crud_app

WORKDIR /crud_app

RUN apt-get update && apt-get install -y sqlite3

COPY requirements.txt .

COPY . .

RUN pip install --upgrade pip && pip install -r requirements.txt

RUN pip install gunicorn

RUN chmod a+x .docker/*.sh

ENTRYPOINT ["bash", ".docker/app.sh"]