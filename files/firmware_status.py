#! /usr/bin/env python3
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 smartindent
# pylint: disable=invalid-name,missing-module-docstring

import os
from datetime import datetime
import subprocess
import json
import yaml
from pkg_resources import packaging

####################################################
# these cfg settings can be set via a cfg file
# placed in the same directory as the script and
# with the same name, but the *.yml extension
# using yaml syntax:
# warn_days: 14
# crit_days: 30
#####################################################
# warn if the outstanding update is older then X days
warn_days = 1
# critical if the outstanding update is older then X days
crit_days = 14
# ignore release candidate versions
ignore_rc = True

cfg_file = '%s.%s' % (os.path.splitext(os.path.abspath(__file__))[0], 'yml',)

try:
    with open(cfg_file, "r") as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.BaseLoader)
        if 'warn_days' in cfg:
            warn_days = int(cfg['warn_days'])
        if 'crit_days' in cfg:
            crit_days = int(cfg['crit_days'])
        if 'ignore_rc' in cfg:
            ignore_rc = bool(cfg['ignore_rc'])
except FileNotFoundError:
    pass

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
