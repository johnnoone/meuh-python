Packaging .deb
==============

https://www.debian.org/doc/manuals/maint-guide/build.en.html


Build Dependencies
------------------

Missing build dependencies can be fetched with ``dpkg-checkbuilddeps``.


In the package source folder::

    sudo mk-build-deps -i -t aptitude

will build, and install with aptitude, a package that pulls the build dependencies you need. mk-build-deps is part of the devscripts package.


Build packages
--------------

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


And then copy::

    cp ../*.deb
    cp ../*.dsc
