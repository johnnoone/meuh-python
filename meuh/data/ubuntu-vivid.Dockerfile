FROM ubuntu:15.04
MAINTAINER Cowgirl MEUH, cowgirl@iscool-e.com
RUN apt-get update && apt-get -y upgrade
RUN apt-get update && apt-get install -y \
        build-essential \
        curl \
        debian-archive-keyring \
        devscripts \
        git \
        equivs \
        vim
