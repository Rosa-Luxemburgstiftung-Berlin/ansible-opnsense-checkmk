#! /usr/bin/env python3
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 smartindent
# pylint: disable=invalid-name,missing-module-docstring

import subprocess
import json
from pkg_resources import packaging

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

pr = subprocess.run(
        ['/usr/local/opnsense/scripts/firmware/changelog.sh', 'list'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True
    )

jverlist = json.loads(pr.stdout)
nextversion = None
latestversion = None
for verd in jverlist:
    if ignore_rc and 'r' in verd['version']:
        continue
    verver = packaging.version.parse(verd['version'])
    if verver <= opnver:
        continue
    nextversion = verd
    latestversion = jverlist[-1]
    break

print(nextversion)
print(latestversion)
#print('%s FIRMWARE %s - %s' % (ecode, status, txt))
