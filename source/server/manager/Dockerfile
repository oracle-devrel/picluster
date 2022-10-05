FROM python:3

ARG WARBLE_SERVER_ARG
ENV WARBLE_SERVER=$WARBLE_SERVER_ARG

RUN pip install requests
ADD server.py server.py
EXPOSE 80
ENTRYPOINT ["python3", "-u", "server.py"]
