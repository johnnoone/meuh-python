FROM debian:7.8
MAINTAINER Cowgirl MEUH, cowgirl@iscool-e.com
RUN echo 'deb http://http.debian.net/debian wheezy-backports main' >> /etc/apt/sources.list
RUN apt-get update && apt-get -y upgrade
RUN apt-get update && apt-get install -y --no-install-recommends \
        apt-utils \
        ca-certificates \
        dialog
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        openssh-client \
        vim \
        wget
RUN apt-get update && apt-get install -y -t wheezy-backports \
        build-essential \
        devscripts \
        equivs \
        git
RUN rm -rf /var/lib/apt/lists/*
