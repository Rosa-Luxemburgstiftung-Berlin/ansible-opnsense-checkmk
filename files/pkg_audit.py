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
vulnack = None
try:
    with open(cfg_file, "r") as ymlfile:
        vulnack = yaml.load(ymlfile, Loader=yaml.BaseLoader)
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

vulns = {}
for package, data in vulnx['packages'].items():
    vulns[package] = {}
    vulns[package]['version'] = data['version']
    vulns[package]['issues'] = []
    for issue in data['issues']:
        vulns[package]['issues'].append(issue['description'])

if vulnack:
    for package, data in vulns.items():
        if package in vulnack:
            for ackeddescr in vulnack[package]['issues']:
                vulns[package]['issues'].remove(ackeddescr)
        if len(vulns[package]['issues']) == 0:
            vulns.pop(package)

unacked = len(vulns)
warntxt = ''
for package, data in vulns.items():
    warntxt += '; '.join(data['issues'])

ecode = 0
status = 'OK'
txt = 'no vulnerable packages found'
if unacked > 0:
    ecode = 1
    status = 'WARNING'
    txt = f'unacknowledged vulnerable packages: {unacked} ({warntxt})'

print(
        '%s PKGAUDIT vulnpackages=%s;;;;|acked=%s;;;; %s - %s' %
        (ecode, vuln_pkg_count, vuln_pkg_count-unacked, status, txt)
    )
