FROM fcollman/render-python
MAINTAINER Forrest Collman (forrest.collman@gmail.com)

RUN mkdir -p /usr/local/render-python-apps
WORKDIR /usr/local
RUN pip install tifffile
RUN pip install opencv-python

COPY . /usr/local/render-python-apps

#RUN git clone http://stash.corp.alleninstitute.org/scm/~forrestc/json_module.git
WORKDIR render-python-apps/json_module
#RUN git pull
RUN python setup.py install

#RUN git clone https://github.com/fcollman/render-python-apps
#WORKDIR render-python-apps
#RUN git pull && git checkout newrender

COPY jupyter_notebook_config.py /root/.jupyter/
WORKDIR /usr/local/render-python-apps
