docker pull atbigdawg:5000/fcollman/render-python:master
docker tag atbigdawg:5000/fcollman/render-python:master fcollman/render-python
docker build -t fcollman/render-python-apps:reorg .
docker tag fcollman/render-python-apps:reorg fcollman/render-python-apps:reorg_testsharmi
#docker push atbigdawg:5000/fcollman/render-python-apps:reorg
docker kill renderapps_testsharmi
docker rm renderapps_testsharmi
docker run -d --name renderapps_testsharmi \
-v /nas2:/nas2 \
-v /nas:/nas \
-v /nas3:/nas3 \
-v /nas4:/nas4 \
-v /data:/data \
-v /pipeline:/pipeline \
-v /data/array_tomography/Sharmi_tools/render-python-apps:/usr/local/render-python-apps \
-v /etc/hosts:/etc/hosts \
-p 9999:9999 \
-e "PASSWORD=$JUPYTERPASSWORD" \
-i -t fcollman/render-python-apps:reorg_testsharmi
 

