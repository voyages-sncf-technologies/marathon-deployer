FROM python:3.6-alpine

ADD requirements.txt /tmp/
ADD marathon_deploy/ /deploytool/
RUN pip3 install -r /tmp/requirements.txt && \
    chmod +x /deploytool/deploytool.py

WORKDIR /deploytool
ENTRYPOINT ["/deploytool/deploytool.py"]