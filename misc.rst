.deb
====

https://www.debian.org/doc/manuals/maint-guide/build.en.html

list missing depencendies
-------------------------

Actually I can use ``dpkg-checkbuilddeps`` which shows the build dependencies. That gets me 99% of what I need.


dpkg-checkbuilddeps?
--------------------

In the package source folder::

    sudo mk-build-deps -i -t aptitude

will build, and install with aptitude, a package that pulls the build dependencies you need. mk-build-deps is part of the devscripts package.


Docker
======

Running a docker
----------------

::
    docker run ubuntu:14.04 /bin/echo 'Hello world'


An Interactive Container
------------------------

::

    sudo docker run -t -i ubuntu:14.04 /bin/bash


image ubuntu:14.04
------------------

Update distrib::

    apt-get update
    apt-get upgrade


and then, install missing building packages::

    apt-get install -y curl build-essential devscripts equivs


Build packages
==============

Prepare the current builder user::

  git config --global user.email "cowgirl@iscool-e.com"
  git config --global user.name "Cowgirl BOT"
  export DEBEMAIL=cowgirl@iscool-e.com
  export DEBFULLNAME="Cowgirl BOT"


Download sources::

    cd /srv
    curl -O http://archive.ubuntu.com/ubuntu/pool/main/n/nginx/nginx_1.4.6.orig.tar.gz
    curl -O http://archive.ubuntu.com/ubuntu/pool/main/n/nginx/nginx_1.4.6-1ubuntu3.1.debian.tar.gz
    curl -O http://archive.ubuntu.com/ubuntu/pool/main/n/nginx/nginx_1.4.6-1ubuntu3.1.dsc


prepare package folder::

    dpkg-source -x nginx_1.4.6-1ubuntu3.1.dsc nginx


install build dependencies::

    cd nginx
    mk-build-deps -ir --tool 'apt-get --no-install-recommends -y'


Build packages::

    dpkg-buildpackage -us -uc


Et copier les builds::

    cp ../*.deb
    cp ../*.dsc
