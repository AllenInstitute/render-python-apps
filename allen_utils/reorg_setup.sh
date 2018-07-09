docker pull localhost:5000/fcollman/render-python:master
docker tag localhost:5000/fcollman/render-python:master fcollman/render-python
docker build -t sharmi/render-python-apps:reorg .
#docker tag fcollman/render-python-apps:reorg fcollman/render-python-apps:reorg_testsharmi
#docker push atbigdawg:5000/fcollman/render-python-apps
docker kill renderapps_develop
docker rm renderapps_develop
docker run -d --name renderapps_develop \
-v /nas2:/nas2 \
-v /nas:/nas \
-v /nas3:/nas3 \
-v /nas4:/nas4 \
-v /data:/data \
-v /pipeline:/pipeline \
-v /pipeline/sharmi/Sharmi_tools/render-python-apps-branches/DEVELOP/render-python-apps:/usr/local/share/render-python-apps \
-v /etc/hosts:/etc/hosts \
-p 7777:7777 \
-e "PASSWORD=$JUPYTERPASSWORD" \
-i -t sharmi/render-python-apps:reorg \
/bin/bash -c "jupyter notebook --config=/root/.jupyter/jupyter_notebook_config.py  --no-browser --allow-root --notebook-dir=/pipeline/sharmi/Sharmi_tools/render-python-apps-branches/DEVELOP/render-python-apps"
