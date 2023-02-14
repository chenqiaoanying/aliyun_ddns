# aliyun_ddns
check public ipv6 per minute and update resolve records on aliyun.

```
docker run -d \
  --name aliyun-ddns \
  --network host \
  -e ALIYUN_ACCESS_KEY_ID=$aliyun_access_key_id \
  -e ALIYUN_ACCESS_SECRET=$aliyun_access_secret \
  -e DOMAIN=nas.xiaowandou.top,ipv6.nas.xiaowandou.top \
  --cap-add NET_ADMIN \
  ghcr.io/chenqiaoanying/aliyun-ddns:latest
```
