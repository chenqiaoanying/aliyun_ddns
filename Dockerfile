FROM python:3.10

RUN apt-get update && apt-get install cron iproute2 -y

# install python package
COPY requirements.txt /requirements.txt
COPY aliyun_ddns /aliyun_ddns
RUN pip install -r /requirements.txt

# add cron job
ENV DDNS_LOG_FILE="/var/log/ddns.log"

COPY ./docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]