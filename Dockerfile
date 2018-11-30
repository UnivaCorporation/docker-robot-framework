FROM python:latest

RUN apt-get -y update &&  apt-get -y install unzip jq

COPY src /project/src/
COPY setup.py /project/

WORKDIR /project
RUN     python setup.py bdist_wheel && pip install --no-cache-dir dist/*.whl
WORKDIR /scratch

CMD pybot --version
