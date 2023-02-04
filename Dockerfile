FROM python:3.10

RUN apt-get update && apt-get install cron iproute2 -y

# install python package
COPY requirements.txt /app/requirements.txt
COPY main.py /app/main.py
COPY aliyun_ddns /app/aliyun_ddns
RUN pip install -r /app/requirements.txt

# add cron job
ENV DDNS_LOG_FILE="/var/log/ddns.log"

COPY ./docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]