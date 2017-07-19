FROM fcollman/render-python
MAINTAINER Forrest Collman (forrest.collman@gmail.com)

RUN mkdir -p /usr/local/render-python-apps
WORKDIR /usr/local
RUN conda install jupyter
RUN pip install tifffile
RUN pip install opencv-python
RUN pip install pandas
RUN pip install matplotlib

RUN apt-get install libspatialindex-dev -y
RUN apt-get install nano -y
COPY . /usr/local/render-python-apps

RUN pip install argschema

#RUN git clone https://github.com/fcollman/render-python-apps
#WORKDIR render-python-apps
#RUN git pull && git checkout newrender
#RUN python setup.py install
COPY jupyter_notebook_config.py /root/.jupyter/
WORKDIR /usr/local/render-python-apps
RUN python setup.py install

CMD ["jupyter", "notebook", "--no-browser", "--allow-root"]
