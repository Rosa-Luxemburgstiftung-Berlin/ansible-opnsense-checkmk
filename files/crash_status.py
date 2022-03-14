#! /usr/bin/env python3
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 smartindent

import glob

c = glob.glob('/var/crash/*')
ecode = 0
status = 'OK'
txt = 'no crashes found'
if len(c) > 0:
    ecode = 2
    status = "ERROR"
    txt = 'detected crash: %s' % ', '.join(c)

print('%s CRASHSTATUS crashes=%s %s - %s' % (ecode, len(c), status, txt))
