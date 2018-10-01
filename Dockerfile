FROM python:latest

RUN apt-get -y update
RUN apt-get -y install unzip

COPY src /project/src/
COPY setup.py /project/

WORKDIR /project
RUN python setup.py bdist_wheel
RUN pip install --no-cache-dir dist/*.whl

CMD pybot --version
