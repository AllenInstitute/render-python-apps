FROM fcollman/render-python
MAINTAINER Forrest Collman (forrest.collman@gmail.com)

RUN mkdir -p /usr/local/render-python-apps
COPY . /usr/local/render-python-apps

#RUN git clone https://github.com/fcollman/render-python-apps
#WORKDIR render-python-apps
#RUN git pull && git checkout newrender
#RUN python setup.py install
COPY jupyter_notebook_config.py /root/.jupyter/
WORKDIR /usr/local/render-python-apps
RUN pip install setuptools --upgrade --disable-pip-version-check
RUN python setup.py install

CMD ["jupyter", "notebook", "--no-browser", "--allow-root"]
