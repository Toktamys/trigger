FROM python:3.8.1

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
COPY requirements.txt ./requirements.txt
COPY ./dockerfiles/docker-entrypoint.sh /

RUN apt-get update && apt-get install -y mc htop default-libmysqlclient-dev
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN rm -rf /var/cache/apt
RUN chmod +x /docker-entrypoint.sh