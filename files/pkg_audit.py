#! /usr/bin/env python3
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 smartindent
# pylint: disable=invalid-name,missing-module-docstring

import os
import subprocess
import json
import yaml

# you can acknowledge each vulnerable package by using a cfg file
# placed in the same directory as the script and with the same name,
# but the *.yml extension using yaml syntax:
# package-name:
#   version: VERSION
#   issues:
#       - issue description as found running `pkg audit`

cfg_file = '%s.%s' % (os.path.splitext(os.path.abspath(__file__))[0], 'yml',)
cfg = None
try:
    with open(cfg_file, "r") as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.BaseLoader)
except FileNotFoundError:
    pass

pr = subprocess.run(
        ['pkg', 'audit', '-F', '--raw=json-compact', '-q'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False
    )
vulnx = json.loads(pr.stdout)
vuln_pkg_count = vulnx['pkg_count']
unacked = vuln_pkg_count

for package, data in vulnx['packages'].items():
    if cfg and package in cfg:
        if cfg[package]['version'] == data['version']:
            issue_count = data['issue_count']
            for issue in data['issues']:
                if issue['description'] in cfg[package]['version']['issues']:
                    issue_count = issue_count - 1
            if issue_count == 0:
                unacked = unacked -1
ecode = 0
status = 'OK'
txt = 'no vulnerable packages found'
if unacked > 0:
    ecode = 1
    status = 'WARNING'
    txt = f'unacknowledged vulnerable packages: {unacked}'

print(
        '%s PKGAUDIT vulnpackages=%s;;;;|acked=%s;;;; %s - %s' %
        (ecode, vuln_pkg_count, vuln_pkg_count-unacked, status, txt)
    )
