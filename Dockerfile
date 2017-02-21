FROM continuumio/anaconda
MAINTAINER Forrest Collman (forrest.collman@gmail.com)
RUN mkdir -p /usr/local/render-python-apps
WORKDIR /usr/local
RUN pip install -e git+https://github.com/fcollman/render-python.git@module#egg=render-python
WORKDIR /usr/local
RUN git clone https://github.com/fcollman/render-python-apps
WORKDIR render-python-apps
RUN git pull && git checkout newrender

