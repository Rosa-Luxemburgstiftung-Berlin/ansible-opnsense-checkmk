#! /usr/bin/env python3
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 smartindent
# pylint: disable=invalid-name,missing-module-docstring

import os
import sys
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
# ignore beta versions
ignore_beta = True
# fetch new changelogs once X day(s)
fetch_changelog_days = 1
# fetch changelog timeout in seconds
fetch_changelog_timeout = 20
# perform a pkg update test
pkg_update_test = True
# timeout for pkg update test
pkg_update_timeout = 20

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
        if 'ignore_beta' in cfg:
            ignore_beta = bool(cfg['ignore_beta'])
        if 'fetch_changelog_days' in cfg:
            fetch_changelog_days = int(cfg['fetch_changelog_days'])
        if 'fetch_changelog_timeout' in cfg:
            fetch_changelog_timeout = int(cfg['fetch_changelog_timeout'])
        if 'pkg_update_test' in cfg:
            pkg_update_test = bool(cfg['pkg_update_test'])
        if 'pkg_update_timeout' in cfg:
            pkg_update_timeout = int(cfg['pkg_update_timeout'])
except FileNotFoundError:
    pass

emsg = ""
today = datetime.today()

# test if we must fetch changelog
fetchchangelog = False
try:
    lastchangelogfetch = os.path.getmtime('/usr/local/opnsense/changelog/index.json')
    ddiff = today - datetime.fromtimestamp(lastchangelogfetch)
    if ddiff.days >= fetch_changelog_days:
        fetchchangelog = True
except OSError:
    fetchchangelog = True

if fetchchangelog:
    try:
        pr = subprocess.run(
                ['/usr/local/opnsense/scripts/firmware/changelog.sh', 'fetch'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=fetch_changelog_timeout,
                check=True
            )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        emsg = " (changelog fetch failed (!))"

pr = subprocess.run(
        ['opnsense-version', '-v'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True
    )
opn_version = pr.stdout.decode().split('_')[0].strip()
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
    if ignore_beta and verd['version'].endswith('b'):
        continue
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
    ddiff = today - nextverdt
    ddiffdays = ddiff.days
    if ddiffdays > crit_days:
        ecode = 2
        status = 'CRITICAL'
    elif ddiffdays > warn_days:
        ecode = 1
        status = 'WARNING'
    txt = 'update %s to %s available since %s days' % (
                            opn_version,
                            nextversion['version'],
                            ddiffdays,
                        )
    if latestversion and not latestversion == nextversion:
        txt = '%s (latest version: %s)' % (txt, latestversion['version'],)

print('%s FIRMWARE - %s - %s %s' % (ecode, status, txt, emsg))

if not pkg_update_test:
    sys.exit(0)

try:
    pr = subprocess.run(
            ['pkg', 'upgrade', '--dry-run'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=pkg_update_timeout,
            check=False
        )
except subprocess.TimeoutExpired:
    print('3 PACKAGES - UNKNOWN - timeout expired')
    sys.exit(0)

pkgcounters = {
        'upgraded':  0,
        'installed': 0,
        'reinstalled': 0,
        'removed': 0,
    }
olines = pr.stdout.splitlines()
pkgperfdata = ''
for pcounter in pkgcounters:
    expectline = 'Number of packages to be %s: ' % pcounter
    for line in olines:
        line = line.decode()
        if line.startswith(expectline):
            pkgcounters[pcounter] = int(line.split(': ')[1])
            break
    if len(pkgperfdata) > 0:
        pkgperfdata = '%s|' % pkgperfdata
    pkgperfdata = '%s%s=%s;;;;' % (pkgperfdata, pcounter, pkgcounters[pcounter])

pkgecode = 0
pkgstatus = 'OK'
pkgtxt = 'all packages up to date'
if pkgcounters['upgraded'] > 0:
    pkgecode = 1
    pkgstatus = 'WARNING'
    pkgtxt = 'packages actions required'
    if ecode > 0:
        pkgecode = 1
        pkgstatus = 'CRITICAL'

print('%s PACKAGES %s %s - %s' % (pkgecode, pkgperfdata, pkgstatus, pkgtxt))
