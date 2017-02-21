docker build -t renderapps:latest .
docker kill renderapps
docker rm renderapps
docker run -d --name renderapps \
-v /nas:/nas \
-v /nas2:/nas2 \
-v /nas3:/nas3 \
-v /nas4:/nas4 \
-v /data:/data \
-v /pipeline:/pipeline \
-v /pipeline/render-python-apps:/usr/local/render-python-apps \
-v /etc/hosts:/etc/hosts \
-it renderapps:latest \
/bin/bash
