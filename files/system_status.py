#! /usr/bin/env python3
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 smartindent
# pylint: disable=invalid-name,missing-module-docstring

import json
import subprocess

pr = subprocess.run(
        ['configctl', 'system', 'status'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True
    )

ecode = 0
status = 'OK'
msg = ''

jo = json.loads(pr.stdout)
for alertitem in jo:
    if msg:
        msg += ' '
    msg += alertitem
    alert = jo[alertitem]
    if ecode == 0:
        ecode = 1
        status = 'WARNING'
    if alert['priority'] > 2:
        ecode = 2
        status = 'CRITICAL'
        status = "ERROR"
    if 'title' in alert:
        if msg:
            msg += ' '
        msg += alert['title']
    if 'message' in alert:
        if msg:
            msg += ' '
        msg += alert['message']

print(f'{ecode} SYSTEM-STATUS - {status} - {msg}')
