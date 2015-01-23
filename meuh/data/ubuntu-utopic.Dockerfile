FROM ubuntu:14.10
MAINTAINER Cowgirl MEUH, cowgirl@iscool-e.com
RUN apt-get update && apt-get -y upgrade
RUN apt-get update && apt-get install -y \
        build-essential \
        curl \
        devscripts \
        git \
        equivs \
        vim
