#! /usr/bin/env python3
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 smartindent
# pylint: disable=invalid-name,missing-module-docstring
import os
import glob

IGNOREFILES = ['minfree', 'bounds',]

g = glob.glob('/var/crash/*')
c = [
    os.path.basename(f) for f in g
    if os.path.splitext(os.path.basename(f))[0] not in IGNOREFILES
        and not os.path.islink(f)
    ]
ecode = 0
status = 'OK'
txt = 'no crashes found'
if len(c) > 0:
    ecode = 2
    status = "ERROR"
    txt = 'detected crash: %s' % ', '.join(c)
else:
    if os.path.exists('/tmp/PHP_errors.log'):
        c = ['/tmp/PHP_errors.log']
        ecode = 1
        status = "WARNING"
        txt = 'detected php crash'

print('%s CRASHSTATUS crashes=%s %s - %s' % (ecode, len(c), status, txt))
