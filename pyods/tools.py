import os
import socket
from pathlib import Path
import re
from subprocess import Popen, STDOUT, PIPE


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('10.255.255.255', 1))
    ip = s.getsockname()[0]
    s.close()
    return ip


def _is_image(filename):
    try:
        ext = os.path.splitext(filename)[1][1:].lower()
    except:
        return False

    if ext in ["iso", "img", "dmg"]:
        return True
    return False


def list_removable_drives():
    script = """grep -Hv ^0$ /sys/block/*/removable |
                sed s/removable:.*$/device\\/uevent/ |
                xargs grep -H ^DRIVER=sd |
                sed s/device.uevent.*$/size/ |
                xargs grep -Hv ^0$ |
                cut -d / -f 4"""


def list_images(path):
    files = list(Path(path).glob('**/*.*'))
    files = [f for f in files if _is_image(f)]
    files.sort()
    return files


def _getdev(line):
    try:
        dev = re.findall('dev=\'(.*?)\'', line)[0]
    except:
        return None
    return dev


def list_optical_drives():
    out = Popen(["wodim", "--devices"], stderr=STDOUT, stdout=PIPE)

    (output, returncode) = out.communicate()[0], out.returncode
    if returncode != 0:
        raise Exception("Failed to execute wodim command return code %d" % returncode)

    drives = [_getdev(l) for l in output.split()]
    drives = [d for d in drives if d is not None]
    drives.sort()
    return drives
