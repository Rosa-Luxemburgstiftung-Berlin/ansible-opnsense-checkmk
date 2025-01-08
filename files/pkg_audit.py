#! /usr/bin/env python3
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 smartindent
# pylint: disable=invalid-name,missing-module-docstring,too-many-ancestors,super-with-arguments

import os
import sys
import subprocess
import argparse
import json
import yaml

__doc__ = """
checkmk local check performing a pkg audit
on freebsd / opnsense
"""

# you can acknowledge each vulnerable package by using a cfg file
# placed in the same directory as the script and with the same name,
# but the *.yml extension using yaml syntax:
# package-name:
#   issues:
#       - issue description as found running `pkg audit`
# example:
# ---
# cyrus-sasl:
#   issues:
#     - cyrus-sasl -- Fix off by one error
# openssl:
#   issues:
#     - OpenSSL -- Infinite loop in BN_mod_sqrt parsing certificates

class MyDumper(yaml.Dumper):
    """simple helper class fixing pyyamls list indent"""
    def increase_indent(self, flow=False, indentless=False):
        return super(MyDumper, self).increase_indent(flow, False)

argparser = argparse.ArgumentParser(description=__doc__)
argparser.add_argument(
    '-c', '--config-file',
    type=str,
    dest='configfile', action='store',
    default='%s.%s' % (os.path.splitext(os.path.abspath(__file__))[0], 'yml',),
    help='path to yaml config file for acknowledging audit vulnerable package'
    )
argparser.add_argument(
    '-p', '--print-config-file',
    action="store_true",
    help='do not perform a real check, just print a current config'
    )

args = argparser.parse_args()

cfg_file = args.configfile
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
if vuln_pkg_count > 0:
    for package, data in vulnx['packages'].items():
        vulns[package] = {}
        vulns[package]['issues'] = []
        for issue in data['issues']:
            vulns[package]['issues'].append(issue['description'].lower())

if args.print_config_file:
    if not vulns:
        print('-'*3)
        print('.'*3)
        sys.exit(0)
    print(
        yaml.dump(
            vulns,
            Dumper=MyDumper,
            sort_keys=True,
            indent=2,
            width=70,
            explicit_start=True,
            explicit_end=True,
            default_flow_style=False
        )
    )
    sys.exit(0)

if vulnack:
    for package in list(vulns.keys()):
        if package in vulnack:
            for ackeddescr in vulnack[package]['issues']:
                ackeddescr = ackeddescr.lower()
                if ackeddescr in vulns[package]['issues']:
                    vulns[package]['issues'].remove(ackeddescr)
        if len(vulns[package]['issues']) == 0:
            vulns.pop(package)

unacked = len(vulns)
unackedissues = []
for package, data in vulns.items():
    for issue in data['issues']:
        unackedissues.append(f'{package}: {issue}')
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
