FROM nvidia/cuda:8.0-cudnn6-devel-ubuntu16.04
MAINTAINER caffe-maint@googlegroups.com

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        cmake \
        git \
        wget \
        libatlas-base-dev \
        libboost-all-dev \
        libgflags-dev \
        libgoogle-glog-dev \
        libhdf5-serial-dev \
        libleveldb-dev \
        liblmdb-dev \
        libopencv-dev \
        libprotobuf-dev \
        libsnappy-dev \
        protobuf-compiler \
        python-dev \
	python-pip \
        python-numpy && \
    rm -rf /var/lib/apt/lists/*

ENV CAFFE_ROOT=/opt/caffe
WORKDIR $CAFFE_ROOT

# FIXME: clone a specific git tag and use ARG instead of ENV once DockerHub supports this.
ENV CLONE_TAG=duburlan-patch-1

RUN git config --global http.sslVerify false && \
    git clone -b ${CLONE_TAG} --depth 1 https://github.com/duburlan/caffe.git . && \
    python -m pip install --upgrade pip && \
    for req in $(cat python/requirements.txt) pydot; do python -m pip install $req; done && \
    cp Makefile.config.example Makefile.config && \
    make -j"$(nproc)" && \
    make py && \
    make test -j8

#RUN python -m pip install --upgrade pip && \
#    wget https://raw.githubusercontent.com/weiliu89/caffe/ssd/python/requirements.txt && \
#    for req in $(cat requirements.txt) pydot; do python -m pip install $req; done

ENV PYCAFFE_ROOT $CAFFE_ROOT/python
ENV PYTHONPATH $PYCAFFE_ROOT:$PYTHONPATH
ENV PATH $CAFFE_ROOT/build/tools:$PYCAFFE_ROOT:$PATH
RUN echo "$CAFFE_ROOT/build/lib" >> /etc/ld.so.conf.d/caffe.conf && ldconfig

WORKDIR /workspace
