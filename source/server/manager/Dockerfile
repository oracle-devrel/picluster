FROM python:3
#FROM ghcr.io/graalvm/graalvm-ce:ol8-java17-22
#RUN gu install python

RUN pip install requests
ADD server.py server.py

EXPOSE 80
ENTRYPOINT ["python3", "-u", "server.py"]
#ENTRYPOINT ["graalpython", "-u", "server.py"]
