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
