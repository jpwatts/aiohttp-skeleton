FROM ubuntu:16.04
MAINTAINER Joel Watts <joel@joelwatts.com>

ENV LC_ALL=C.UTF-8 LANG=C.UTF-8

RUN apt-get update

RUN apt-get install -y autoconf
RUN apt-get install -y build-essential
RUN apt-get install -y python3-dev
RUN apt-get install -y python3-virtualenv

ENV PIP_REQUIRE_VIRTUALENV=true

WORKDIR /

RUN python3 -m virtualenv --python=python3 virtualenv

ADD requirements.pip /skeleton/requirements.pip
RUN /virtualenv/bin/python3 -m pip install -r /skeleton/requirements.pip

ADD . /skeleton
RUN /virtualenv/bin/python3 -m pip install -e /skeleton
RUN ln -s /virtualenv/bin/skeleton /usr/local/bin/skeleton
RUN echo 'eval "$(_DAXBOT_COMPLETE=source skeleton)"' >> /root/.bashrc
