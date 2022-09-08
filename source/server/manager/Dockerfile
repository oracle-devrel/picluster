# docker pull ghcr.io/graalvm/graalvm-ce:ol8-java17-22

FROM ghcr.io/graalvm/graalvm-ce:ol8-java17-22

RUN microdnf install patch
RUN gu install python
RUN graalpython -m venv graalenv
RUN . graalenv/bin/activate && pip install --no-cache-dir requests chardet

ADD server.py server.py

EXPOSE 80

CMD . graalenv/bin/activate && exec graalpython server.py
