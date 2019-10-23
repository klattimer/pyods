[Home](README.md)

# Installation

If you're using debian/raspbian/ubuntu installation is easiest via a .deb package.

    dpkg -i pyods_0.1-1_any.deb

At least, once I've figured out how to make it work without including an architecture...

## Building a deb file

    git clone http://github.com/klattimer/pyods.git
    cd pyods
    dpkg-buildpackage -us -uc -b

## Installing on a non-debian system

    git clone http://github.com/klattimer/pyods.git
    cd pyods
    python setup.py install
