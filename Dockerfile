# Set the base image to Ubuntu
FROM python:2.7

# File Author / Maintainer
MAINTAINER Wesley Stratton <stratton.wesley@gmail.com>

ADD reqs.txt /app/reqs.txt
WORKDIR /app/
RUN pip install -r reqs.txt