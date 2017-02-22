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
-p 8888:8888 \
-e "PASSWORD=$JUPYTERPASSWORD" \
-i -t renderapps:latest \
/bin/bash -c "/opt/conda/bin/jupyter notebook --config=/root/.jupyter/jupyter_notebook_config.py --notebook-dir=/pipeline/render-python-apps --no-browser" 
 

