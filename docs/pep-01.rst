PEP 01: Share published packages
================================

:state: done

Goals
-----

* Share published packages between bots with a local repository.


Workflow
--------

1. develop

        do stuff into work_dir

2. build

        copy src from work_dir into build_dir
        build src

3. publish

        copy ``*.deb``, ``*.dsc`` ... from build_dir into publish_dir

        expose all ``*.deb`` found in publish_dir in the local repo


How to create a local Repo ?
----------------------------

::

    PUBLISH_DIR=/usr/local/mydebs
    apt-get -y install dpkg-dev gzip
    mkdir -p $PUBLISH_DIR
    cd /usr/local/mydebs
    dpkg-scanpackages . /dev/null | gzip -9c > Packages.gz
    cat 'deb file:$PUBLISH_DIR ./' > /etc/apt/sources.list.d/meuh.list
    apt-get update
