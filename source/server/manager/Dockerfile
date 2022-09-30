FROM python:3
RUN pip install requests
ADD server.py server.py
EXPOSE 80
ENTRYPOINT ["python3", "-u", "server.py"]
