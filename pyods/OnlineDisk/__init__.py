import os
from enum import Enum, auto
from subprocess import Popen, STDOUT, PIPE
import re


class OnlineDiskState(Enum):
    READY = auto()
    NOT_READY = auto()
    OPEN = auto()
    EMPTY = auto()


class OnlineDisk:
    def __init__(self, filename):
        self._filename = filename
        self._size = 0
        self._label = None
        self._state = OnlineDiskState.EMPTY

    @property
    def exists(self):
        return False

    @property
    def state(self):
        return self._state

    @property
    def filename(self):
        return self._filename

    @property
    def size(self):
        return self._size

    @property
    def label(self):
        return self._label

    def erase(self):
        pass

    def eject(self):
        pass

    def read(self, start, end):
        return b''

    def __repr__(self):
        return hash('%s:%d'(self.label, self.size))

    def serialise(self):
        return {
            'label': self.label,
            'size': self.size,
            'filename': str(self.filename),
            'state': str(self.state)
        }


class DiskImage(OnlineDisk):
    def __init__(self, filename):
        super(DiskImage, self).__init__(filename)
        if self.exists:
            self._state = OnlineDiskState.READY

    @property
    def exists(self):
        return os.path.exists(self.filename)

    @property
    def size(self):
        if self._size == 0 and self.exists:
            self._size = os.stat(self.filename).st_size
        return self._size

    @property
    def label(self):
        if self._label is None:
            out = Popen(["isoinfo", "-d", '-i', self.filename], stderr=STDOUT, stdout=PIPE)

            (output, returncode) = out.communicate()[0].lower(), out.returncode
            if returncode != 0:
                raise Exception("Failed to execute isoinfo command return code %d" % returncode)

            for line in output.split(b'\n'):
                if line.startswith(b'volume id:') and len(line) > 11:
                    self._label = line[11:].decode("utf-8")
                    break

        return self._label

    def erase(self):
        # os.unlink ...
        pass

    def read(self, start, end):
        if end == 0:
            end = self.size - 1

        if end > self.size - 1:
            raise Exception("end address exceeds size by %d bytes" % (end - (self.size - 1)))

        if start > end:
            raise Exception("start address exceeds end address %d > %d" % (start, end))

        len = end - start + 1

        with open(self.filename, "rb") as f:
            f.seek(start)
            data = f.read(len)
        return data


class OpticalDrive(OnlineDisk):
    def __init__(self, filename):
        super(OpticalDrive, self).__init__(filename)
        self._type_re = re.compile('type \d*?')
        self._block_size = 0
        self._vol_size = 0

    @property
    def state(self):
        old_state = self._state
        out = Popen(["setcd", "-i", self.filename], stderr=STDOUT, stdout=PIPE)
        (output, returncode) = out.communicate()[0].lower(), out.returncode
        if returncode != 0:
            raise Exception("Failed to execute setcd command return code %d" % returncode)

        if b'is open' in output:
            self._state = OnlineDiskState.OPEN

        if b'not ready' in output:
            self._state = OnlineDiskState.NOT_READY

        if b'disc found' in output:
            # 'Disc found in drive: data disc type 1'
            self._type = int(self._type_re.findall(output))

            # TODO Extract type
            self._state = OnlineDiskState.READY

        if b'no disc' in output:
            self._state = OnlineDiskState.EMPTY

        if old_state != self._state:
            # Change handler...

            self._size = 0
            self._label = None
        return self._state

    @property
    def label(self):
        if self._label is None:
            out = Popen(["isoinfo", "-d", '-i', self.filename], stderr=STDOUT, stdout=PIPE)

            (output, returncode) = out.communicate()[0].lower(), out.returncode
            if returncode != 0:
                raise Exception("Failed to execute isoinfo command return code %d" % returncode)

            for line in output.split(b'\n'):
                if line.startswith(b'volume id:') and len(line) > 11:
                    self._label = line[11:].decode("utf-8")
                    break

        return self._label

    @property
    def block_size(self):
        return (self._block_size, self._vol_size)

    @property
    def size(self):
        if self._size == 0:
            out = Popen(["isoinfo", "-d", '-i', self.filename], stderr=STDOUT, stdout=PIPE)

            (output, returncode) = out.communicate()[0].lower(), out.returncode
            if returncode != 0:
                raise Exception("Failed to execute isoinfo command return code %d" % returncode)

            for line in output.split(b'\n'):
                if line.startswith(b'volume size is:') and len(line) > 16:
                    self._vol_size = line[16:]

                if line.startswith(b'logical block size is:') and len(line) > 23:
                    self._block_size = line[23:]
        self._size = self._vol_size * self._block_size

        return self._size

    def erase(self):
        # erase disk
        # check if re-writable media is in first
        pass

    def eject(self):
        pass

    def read(self, start, end):
        if end == 0:
            end = self.size - 1

        if end > self.size - 1:
            raise Exception("end address exceeds size by %d bytes" % (end - (self.size - 1)))

        if start > end:
            raise Exception("start address exceeds end address %d > %d" % (start, end))

        len = end - start + 1

        with open(self.filename, "rb") as f:
            f.seek(start)
            data = f.read(len)
        return data


class RemovableDrive(OnlineDisk):
    @property
    def label(self):
        if self._label is None:
            # Get the label of the removable drive or, the label of the first partition
            pass
        return self._label

    @property
    def exists(self):
        return os.path.exists(self.filename)

    def erase(self):
        # erase disk
        pass

    def eject(self):
        pass

    def read(self, start, end):
        if end == 0:
            end = self.size - 1

        if end > self.size - 1:
            raise Exception("end address exceeds size by %d bytes" % (end - (self.size - 1)))

        if start > end:
            raise Exception("start address exceeds end address %d > %d" % (start, end))

        len = end - start + 1

        with open(self.filename, "rb") as f:
            f.seek(start)
            data = f.read(len)
        return data
