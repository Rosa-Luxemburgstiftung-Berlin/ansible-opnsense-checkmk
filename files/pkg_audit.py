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
# example:
# ---
# cyrus-sasl:
#   version: 2.1.27_2
#   issues:
#     - cyrus-sasl -- Fix off by one error
# openssl:
#   version: 1.1.1m_1,1
#   issues:
#     - OpenSSL -- Infinite loop in BN_mod_sqrt parsing certificates

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
    for package in list(vulns.keys()):
        if package in vulnack:
            for ackeddescr in vulnack[package]['issues']:
                if ackeddescr in vulns[package]['issues']:
                    vulns[package]['issues'].remove(ackeddescr)
        if len(vulns[package]['issues']) == 0:
            vulns.pop(package)

unacked = len(vulns)
unackedissues = []
for package, data in vulns.items():
    for issue in data['issues']:
        unackedissues.append(issue)
warntxt = '; '.join(unackedissues)

ecode = 0
status = 'OK'
txt = 'no vulnerable packages found'
if vuln_pkg_count > 0:
    txt = 'no unacknowledged vulnerable packages found'
if unacked > 0:
    ecode = 1
    status = 'WARNING'
    txt = f'unacknowledged vulnerable packages: {unacked} ({warntxt})'

print(
        '%s PKGAUDIT vulnpackages=%s;;;;|acked=%s;;;; %s - %s' %
        (ecode, vuln_pkg_count, vuln_pkg_count-unacked, status, txt)
    )
