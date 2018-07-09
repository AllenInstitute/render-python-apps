conda create --name render-python-apps --prefix $IMAGE_PROCESSING_DEPLOY_PATH python=2.7
source activate render-python-apps
pip install -r ../requirements.txt
