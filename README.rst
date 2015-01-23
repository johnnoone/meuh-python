Meuh
====


Meuh provides some glue between dpkg, docker and debian packaging.

Install
-------

Meuh relies on python-2.7, rsync, and docker up and running.

Lets install it::

    git clone git@github.com:johnnoone/meuh-python.git
    cd meuh-python
    python setup.py install
    cp examples/meuh.cfg ~/.meuh.cfg


And check that is working::

    meuh settings


Quick example
-------------

Let's try to build nginx.

Download the sources::

    apt-get source nginx
    cd nginx*


And build it for wheezy with pierre::

    meuh build pierre
    ll /srv/meuh/publishes/wheezy


Build it also for trusty with paul::

    meuh build paul
    ll /srv/meuh/publishes/trusty
