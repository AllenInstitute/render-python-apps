#docker pull atbigdawg:5000/fcollman/render-python:latest
#docker tag atbigdawg:5000/fcollman/render-python:latest fcollman/render-python:latest
docker build -t fcollman/render-python-apps .
docker tag fcollman/render-python-apps atbigdawg:5000/fcollman/render-python-apps
docker push atbigdawg:5000/fcollman/render-python-apps
docker kill renderapps
docker rm renderapps
docker run -t --name renderapps \
-v /nas:/nas \
-v /nas2:/nas2 \
-v /nas3:/nas3 \
-v /nas4:/nas4 \
-v /nas5:/nas5 \
-v /data:/data \
-v /pipeline:/pipeline \
-v /pipeline/render-python-apps:/usr/local/render-python-apps \
-v /etc/hosts:/etc/hosts \
-p 7777:7777 \
-e "PASSWORD=$JUPYTERPASSWORD" \
-i -t fcollman/render-python-apps 
