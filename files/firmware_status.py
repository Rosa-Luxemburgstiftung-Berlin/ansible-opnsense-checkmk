#! /usr/bin/env python3
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 smartindent
# pylint: disable=invalid-name,missing-module-docstring

from datetime import datetime
import subprocess
import json
from pkg_resources import packaging

# TODO: make this configurable via a cfg file
warn_days = 1
crit_days = 14
ignore_rc = True

pr = subprocess.run(
        ['opnsense-version', '-v'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True
    )
opn_version = pr.stdout.decode().split('_')[0]
opnver = packaging.version.parse(opn_version)

ecode = 0
status = 'OK'
txt = 'version %s is up to date' % opn_version
nextversion = None
latestversion = None

pr = subprocess.run(
        ['/usr/local/opnsense/scripts/firmware/changelog.sh', 'list'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True
    )

jverlist = json.loads(pr.stdout)
for verd in jverlist:
    if ignore_rc and 'r' in verd['version']:
        continue
    verver = packaging.version.parse(verd['version'])
    if verver <= opnver:
        continue
    nextversion = verd
    latestversion = jverlist[-1]
    break

if nextversion:
    nextverdt = datetime.strptime(nextversion['date'], '%B %d, %Y')
    today = datetime.today()
    ddiff = today - nextverdt
    ddiffdays = ddiff.days
    if ddiffdays > crit_days:
        ecode = 2
        status = 'CRITICAL'
    elif ddiffdays > warn_days:
        ecode = 1
        status = 'WARNING'
    txt = 'update to %s available since %s days' % (nextversion['version'], ddiffdays,)
    if latestversion and not latestversion == nextversion:
        txt = '%s (latest version: %s)' % (txt, latestversion['version'],)

print('%s FIRMWARE - %s - %s' % (ecode, status, txt))
