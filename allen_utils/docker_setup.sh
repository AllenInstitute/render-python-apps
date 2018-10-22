#docker pull atbigdawg:5000/fcollman/render-python:latest
#docker tag atbigdawg:5000/fcollman/render-python:latest fcollman/render-python:latest
docker build -t fcollman/render-python-apps .
docker kill renderapps_multchan
docker rm renderapps_multchan
docker run -t --name renderapps_multchan \
-v /nas:/nas \
-v /nas2:/nas2 \
-v /nas3:/nas3 \
-v /nas4:/nas4 \
-v /nas5:/nas5 \
-v /data:/data \
-v /pipeline:/pipeline \
-v /pipeline/Forrest/render-python-apps:/usr/local/render-python-apps \
-v /pipeline/render-modules:/shared/render-modules \
-v /etc/hosts:/etc/hosts \
-p 7778:7777 \
-e "PASSWORD=$JUPYTERPASSWORD" \
-i -t fcollman/render-python-apps 
