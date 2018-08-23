FROM docker.aibs-artifactory.corp.alleninstitute.org/fcollman/render-modules:master
MAINTAINER Forrest Collman (forrest.collman@gmail.com)
RUN mkdir -p /usr/local/render-python-apps
WORKDIR /usr/local/render-python-apps
COPY requirements.txt /usr/local/render-python-apps
RUN pip install -r requirements.txt
RUN pip install setuptools --upgrade --disable-pip-version-check
RUN pip install argschema --upgrade --disable-pip-version-check
RUN pip install jupyter
RUN apt-get update && apt-get install libspatialindex-dev -y
RUN conda install nomkl
COPY . /usr/local/render-python-apps

WORKDIR /shared/render-modules
RUN pip install .
WORKDIR /usr/local/render-python-apps


#RUN git clone https://github.com/fcollman/render-python-apps
#WORKDIR render-python-apps
#RUN git pull && git checkout newrender
#RUN python setup.py install
COPY jupyter_notebook_config.py /root/.jupyter/


RUN python setup.py install

CMD ["jupyter", "notebook", "--no-browser", "--allow-root"]
