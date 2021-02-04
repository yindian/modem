from __future__ import print_function
import os
import select
import shutil
import subprocess
import sys
try:
    from io import BytesIO
except ImportError:
    from StringIO import StringIO as BytesIO
import tempfile
from xmodem import *

def run(modem='xmodem'):

    if modem.lower().startswith('xmodem'):
        pipe   = subprocess.Popen(['sz', '--xmodem', '--quiet', __file__],
                     bufsize=0,
                     stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        si, so = (pipe.stdin, pipe.stdout)

        stream = BytesIO()

    elif modem.lower() == 'ymodem':
        pipe   = subprocess.Popen(['sz', '--ymodem', '--quiet', __file__],
                     bufsize=0,
                     stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        si, so = (pipe.stdin, pipe.stdout)

        stream = BytesIO()

    def getc(size, timeout=3):
        assert pipe.returncode is None
        w,t,f = select.select([so], [], [], timeout)
        if w:
            data = so.read(size)
        else:
            data = None

        print('getc(', repr(data), ')')
        return data

    def putc(data, timeout=3):
        assert pipe.returncode is None
        w,t,f = select.select([], [si], [], timeout)
        if t:
            si.write(data)
            si.flush()
            size = len(data)
        else:
            size = None

        print('putc(', repr(data), repr(size), ')')
        return size

    if modem.lower().startswith('xmodem'):
        xmodem = globals()[modem.upper()](getc, putc)
        nbytes = xmodem.recv(stream, retry=8)
        sys.stdout.flush()
        print('received', nbytes, 'bytes', file=sys.stderr)
        print(stream.getvalue(), file=sys.stderr)

    elif modem.lower() == 'ymodem':
        ymodem = globals()[modem.upper()](getc, putc)
        basedr = tempfile.mkdtemp()
        nfiles = ymodem.recv(basedr, retry=8)
        sys.stdout.flush()
        print('received', nfiles, 'files in', basedr, file=sys.stderr)
        print(subprocess.Popen(['ls', '-al', basedr],
            stdout=subprocess.PIPE).communicate()[0], file=sys.stderr)
        shutil.rmtree(basedr)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        for modem in sys.argv[1:]:
            run(modem.upper())
    else:
        for modem in ['XMODEM', 'YMODEM']:
            run(modem)
