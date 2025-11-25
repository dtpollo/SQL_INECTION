FROM mysql:8

ENV MYSQL_ROOT_PASSWORD=rootpassword
ENV MYSQL_DATABASE=testdb

COPY init.sql /docker-entrypoint-initdb.d/

