FROM ubuntu:latest
MAINTAINER Scott Deng <scottdeng@live.cn>
ENV DEBIAN_FRONTEND noninteractive
ENV PG_VERSION 9.4
ENV PG_CONF /etc/postgresql/$PG_VERSION/main/postgresql.conf
ENV PG_HBA /etc/postgresql/$PG_VERSION/main/pg_hba.conf
ENV PG_DIR /var/lib/postgresql/$PG_VERSION/main
#Update
RUN apt-get update
RUN apt-get upgrade -y

#Install proper dependencies
RUN apt-get install -y git wget
#add repo
RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ trusty-pgdg main" > "/etc/apt/sources.list.d/pgdg.list"
RUN wget --quiet -O - http://apt.postgresql.org/pub/repos/apt/ACCC4CF8.asc | apt-key add -
RUN apt-get update
#Clone the source
RUN git clone https://github.com/DengYiping/open-event-orga-server.git
#cd into the dir
WORKDIR open-event-orga-server
#run the script
RUN apt-get install -y build-essential python python-dev python-setuptools python-pip
RUN apt-get install -y libxml2-dev libxslt1-dev
RUN apt-get install -y nginx uwsgi uwsgi-plugin-python
RUN apt-get install -y postgresql-$PG_VERSION postgresql-contrib-$PG_VERSION libpq-dev
#apt-get -y install postgresql-9.4 postgresql-contrib-9.4
RUN sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" "/etc/postgresql/$PG_VERSION/main/postgresql.conf"
RUN echo "host    all             all             all                     md5" >> "/etc/postgresql/$PG_VERSION/main/pg_hba.conf"
RUN echo "client_encoding = utf8" >> "/etc/postgresql/$PG_VERSION/main/postgresql.conf"
RUN service postgresql restart
RUN localedef -v -c -i en_US -f UTF-8 en_US.UTF-8; exit 0
RUN apt-get install -y postgresql postgresql-contrib libpq-dev
RUN service postgresql restart
#add database user
USER postgres
RUN /etc/init.d/postgresql start \
    && psql --command "CREATE USER open_event_user WITH PASSWORD 'start';" \
    && psql --command "CREATE DATABASE test WITH OWNER=open_event_user LC_COLLATE='en_US.utf8' LC_CTYPE='en_US.utf8' ENCODING='UTF8' TEMPLATE=template0;"
USER root

RUN export DATABASE_URL=postgresql://open_event_user:start@localhost:5432/test
#install dependencies
RUN pip install -r requirements.txt
#create db
RUN python create_db.py
#set environment
RUN echo "export DATABASE_URL=$DATABASE_URL" >> /open-event-orga-server/.bashrc
EXPOSE 80 5000
RUN chmod 0755 *.sh
ENTRYPOINT ["./run.sh"]
