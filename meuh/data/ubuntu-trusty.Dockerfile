FROM ubuntu:14.04
MAINTAINER Cowgirl MEUH, cowgirl@iscool-e.com

# Set the env variables to non-interactive
ENV DEBIAN_FRONTEND=noninteractive \
    DEBIAN_PRIORITY=critical \
    DEBCONF_NOWARNINGS=yes

RUN echo 'deb http://archive.ubuntu.com/ubuntu/ trusty-backports main restricted universe multiverse' >> /etc/apt/sources.list
RUN echo 'deb-src http://archive.ubuntu.com/ubuntu/ trusty-backports main restricted universe multiverse' >> /etc/apt/sources.list
RUN apt-get update && apt-get -y upgrade && apt-get install -y \
        build-essential \
        curl \
        debian-archive-keyring \
        devscripts \
        git \
        equivs \
        vim
