FROM python:latest

COPY src /project/src/
COPY setup.py /project/

WORKDIR /project
RUN python setup.py bdist_wheel
RUN pip install --no-cache-dir dist/*.whl

ENTRYPOINT ["pybot"]

CMD ["--version" ]
