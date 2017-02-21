FROM continuumio/anaconda
MAINTAINER Forrest Collman (forrest.collman@gmail.com)
RUN mkdir -p /usr/local/render-python-apps
WORKDIR /usr/local
RUN git clone https://github.com/fcollman/render-python
WORKDIR render-python
RUN git pull && git checkout module
RUN python setup.py install
WORKDIR /usr/local
RUN git clone https://github.com/fcollman/render-python-apps
WORKDIR render-python-apps
