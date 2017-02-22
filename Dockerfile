FROM fcollman/renderpython
MAINTAINER Forrest Collman (forrest.collman@gmail.com)

RUN mkdir -p /usr/local/render-python-apps
WORKDIR /usr/local
RUN git clone https://github.com/fcollman/render-python-apps
WORKDIR render-python-apps
RUN git pull && git checkout newrender
