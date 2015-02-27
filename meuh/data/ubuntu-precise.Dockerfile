FROM ubuntu:12.04
MAINTAINER Cowgirl MEUH, cowgirl@iscool-e.com

# Set the env variables to non-interactive
ENV DEBIAN_FRONTEND=noninteractive \
    DEBIAN_PRIORITY=critical \
    DEBCONF_NOWARNINGS=yes

RUN echo 'deb http://archive.ubuntu.com/ubuntu/ precise-backports main restricted universe multiverse' >> /etc/apt/sources.list
RUN echo 'deb-src http://archive.ubuntu.com/ubuntu/ precise-backports main restricted universe multiverse' >> /etc/apt/sources.list
RUN apt-get update && apt-get -y upgrade
RUN apt-get update && apt-get install -y \
        aptitude \
        build-essential \
        curl \
        debian-archive-keyring \
        devscripts \
        equivs \
        git
