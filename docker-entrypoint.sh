#!/bin/bash
#set -e

touch "${DDNS_LOG_FILE}" && chmod 0666 "${DDNS_LOG_FILE}"

if [ ! "$ALIYUN_ACCESS_KEY_ID" ] && [ -f /run/secrets/aliyun_access_key_id ]; then
  ALIYUN_ACCESS_KEY_ID=$(cat /run/secrets/aliyun_access_key_id)
fi

if [ ! "$ALIYUN_ACCESS_SECRET" ] && [ -f /run/secrets/aliyun_access_secret ]; then
  ALIYUN_ACCESS_SECRET=$(cat /run/secrets/aliyun_access_secret)
fi

{
  echo "SHELL=/bin/sh"
  echo "PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin"
  echo "*/1 * * * * root python /app/main.py --key $ALIYUN_ACCESS_KEY_ID --secret $ALIYUN_ACCESS_SECRET ${DOMAIN//,/ } >> ${DDNS_LOG_FILE} 2>&1"
} >/etc/crontab

exec cron &
tail -f "$DDNS_LOG_FILE"
