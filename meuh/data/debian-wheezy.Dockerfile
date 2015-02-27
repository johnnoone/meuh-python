FROM debian:7.8
MAINTAINER Cowgirl MEUH, cowgirl@iscool-e.com

# Set the env variables to non-interactive
ENV DEBIAN_FRONTEND=noninteractive \
    DEBIAN_PRIORITY=critical \
    DEBCONF_NOWARNINGS=yes

RUN echo 'deb http://http.debian.net/debian wheezy-backports main' >> /etc/apt/sources.list
RUN echo 'deb-src http://http.debian.net/debian wheezy main' >> /etc/apt/sources.list
RUN echo 'deb-src http://http.debian.net/debian wheezy-updates main' >> /etc/apt/sources.list
RUN echo 'deb-src http://security.debian.org wheezy/updates main' >> /etc/apt/sources.list
RUN echo 'deb-src http://http.debian.net/debian wheezy-backports main' >> /etc/apt/sources.list

RUN apt-get update && apt-get -y upgrade
RUN apt-get update && apt-get install -y --no-install-recommends \
        apt-utils \
        aptitude \
        build-essential \
        ca-certificates \
        ca-certificates-java \
        curl \
        devscripts \
        dialog \
        equivs \
        git \
        openssh-client \
        patch \
        patchutils \
        vim \
        wget
# RUN rm -rf /var/lib/apt/lists/*
