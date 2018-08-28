FROM python:latest

WORKDIR /tests

RUN pip install --no-cache-dir robotframework requests robotframework-requests

ENTRYPOINT ["robot"]

CMD ["--version" ]
