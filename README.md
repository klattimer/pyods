# PyODS
### An Online Disk Server written in python

The Python Online Disk Server allows you to serve cd/dvd/bluray optical drives and iso images to multiple Mac OS
clients on a network. PyODS shares (without credentials at present) all images found in a specified root folder,
and all optical drives attached to the system.

This emulates the network CD rom feature in Mac OS and allow other operating systems to provide access to disks
and disk images via this protocol. The client is found in the Remote Disc section of Finder. Multiple drives and
images can be shared at the same time, images can be uploaded and stored on the server via a RESTful API.

If you're looking for how to share your ubuntu cd drive to a mac, this is probably what you want.

For more information take a look at apple's support article here: https://support.apple.com/en-gb/HT203973

## Server API

### MacOS required API


    Method      HEAD
    Path        /<disk>.dmg   
    User-Agent  CCURLBS::statImage

Retrieves information regarding the disk size it works the same for images or optical drives attached
to the system.

    Method      GET
    Path        /<disk>.dmg
    Range       bytes=(\d*?)-(\d*)   
    User-Agent  CCURLBS::readDataFork

Retrieves a chunk of data from the disk, read as a block device.

NB: There are a number of other endpoints and file accesses which occur on the server, which the server
gracefully returns what is asked for or, a 404 error. This seems to work appropriately in most situations
however Apple may change their mind in the future.

### Extended Image API

    Method      GET
    Path        /images

List the disks on the server in JSON format

    Method      POST
    Path        /images
    Data        Multipart encoded file upload

Upload a file to the image storage, this will fail if the user does not have write access to that folder.

    Method      DELETE
    Path        /images/image.dmg

Delete an image file from the server.

### Extended JSON RPC API (in progress)

I've extended the MacOS API so we can do some nifty things in the future, like burning discs
ripping discs, uploading and sharing disc images on the local network, that sort of deal.
The goal here is to make CD/DVD media supportable in the future, and more useful than ever.

    Method      JSONRPC
    Path        /optical/<disk>
    RPC Method  open

Open the CD/DVD tray.

    Method      JSONRPC
    Path        /optical/<disk>
    RPC Method  close

Close the CD/DVD tray (if possible, slot drives won't always react).

    Method      JSONRPC
    Path        /burn/<disk image>/<disk target>
    RPC Method  burn

Tries to burn an image referenced by it's disk id to a target optical drive referenced by it's disk id

    Method      JSONRPC
    Path        /burn/<disk>
    RPC Method  erase

Tries to erase a CD-RW/DVD-RW found in the drive

    Method      JSONRPC
    Path        /backup/<disk>/<image>
    RPC Method  store

Backup an optical disc to an image file.

    Method      JSONRPC
    Path        /backup/<disk>/<callback url>/<target size>
    RPC Method  dvdencode

Backup a DVD movie to an MP4 file

    Method      JSONRPC
    Path        /backup/<disk>/<callback url>
    RPC Method  cdencode

Backup an audio cd to flac files


## To build a debian package

    dpkg-buildpackage -us -uc -b
