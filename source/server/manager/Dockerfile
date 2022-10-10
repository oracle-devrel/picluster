FROM ghcr.io/graalvm/graalvm-ce:ol8-java17-22

ARG WARBLE_SERVER_ARG
ENV WARBLE_SERVER=$WARBLE_SERVER_ARG

ARG WARBLE_OUTGOING_SERVER_ARG
ENV WARBLE_OUTGOING_SERVER=$WARBLE_OUTGOING_SERVER_ARG

RUN microdnf install patch
RUN gu install python
RUN graalpython -m venv graalenv
RUN . graalenv/bin/activate && pip install --no-cache-dir requests chardet

ADD server.py server.py

EXPOSE 80

CMD . graalenv/bin/activate && exec graalpython server.py


#FROM python:3
#
#ARG WARBLE_SERVER_ARG
#ENV WARBLE_SERVER=$WARBLE_SERVER_ARG
#
#ARG WARBLE_OUTGOING_SERVER_ARG
#ENV WARBLE_OUTGOING_SERVER=$WARBLE_OUTGOING_SERVER_ARG
#
#RUN pip install requests
#ADD server.py server.py
#EXPOSE 80
#ENTRYPOINT ["python3", "-u", "server.py"]
