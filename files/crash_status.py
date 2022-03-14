#! /usr/bin/env python3
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 smartindent

import os
import glob

IGNOREFILES = ['minfree', 'minfree.gz', 'bounds', 'bounds.gz',]

g = glob.glob('/var/crash/*')
c = [ os.path.basename(f) for f in g if os.path.basename(f) not in IGNOREFILES and not os.path.islink(f)]
ecode = 0
status = 'OK'
txt = 'no crashes found'
if len(c) > 0:
    ecode = 2
    status = "ERROR"
    txt = 'detected crash: %s' % ', '.join(c)

print('%s CRASHSTATUS crashes=%s %s - %s' % (ecode, len(c), status, txt))
