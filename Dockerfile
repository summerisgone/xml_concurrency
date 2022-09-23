FROM python:alpine
RUN adduser -D worker
USER worker
WORKDIR /src
ADD . /src

CMD ["python", "-m", "unittest", "parse_test.py"]
