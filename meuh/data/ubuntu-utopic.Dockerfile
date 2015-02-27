FROM ubuntu:14.10
MAINTAINER Cowgirl MEUH, cowgirl@iscool-e.com

# Set the env variables to non-interactive
ENV DEBIAN_FRONTEND=noninteractive \
    DEBIAN_PRIORITY=critical \
    DEBCONF_NOWARNINGS=yes

RUN apt-get update && apt-get -y upgrade && apt-get install -y \
        aptitude \
        build-essential \
        curl \
        debian-archive-keyring \
        devscripts \
        git \
        equivs \
        vim
