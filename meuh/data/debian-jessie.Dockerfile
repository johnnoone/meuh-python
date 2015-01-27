FROM debian:8.0
MAINTAINER Cowgirl MEUH, cowgirl@iscool-e.com
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
RUN apt-get update && apt-get install -y \
        build-essential \
        devscripts \
        equivs \
        git
RUN rm -rf /var/lib/apt/lists/*
