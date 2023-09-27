[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](http://www.gnu.org/licenses/gpl-3.0)
[![ansible-lint](https://github.com/Rosa-Luxemburgstiftung-Berlin/ansible-opnsense-checkmk/actions/workflows/lint.yml/badge.svg?branch=main)](https://github.com/Rosa-Luxemburgstiftung-Berlin/ansible-opnsense-checkmk/actions/workflows/lint.yml)
[![pylint](https://github.com/Rosa-Luxemburgstiftung-Berlin/ansible-opnsense-checkmk/actions/workflows/pylint.yml/badge.svg?branch=main)](https://github.com/Rosa-Luxemburgstiftung-Berlin/ansible-opnsense-checkmk/actions?query=workflow%3Apylint)

# ansible-opnsense-checkmk

Ansible role installing [check_mk](https://checkmk.com/) agent on [opnsense](https://opnsense.org/).

## Local Checks
The role includes some local checks:

### gateway status

Check all configured gateways; one check is created per configured gateway

Sample output:
```
GWSTATUS-GW-WAN OK - GW_WAN (192.168.1.1) : Online
```

### crash detection

Check if a crash placed some file in `/var/crash/`;

Sample output:
```
0 CRASHSTATUS crashes=0 OK - no crashes found
```

### firmware and package update status

Check if there are some updates available;

Sample output:
```
FIRMWARE OK - update 23.1.2 to 23.1.3 available since 1 days
PACKAGES WARNING - packages actions required
```
This check can be configured using a file `/usr/local/lib/check_mk_agent/local/firmware_status.yml`.
You can distribute this file by defining
```
opn_check_mk_additional_files:
  firmware_status.yml: "{{ opn_check_mk_lib_dir }}/local/"
```
Configurable vars:
  * `warn_days`: warn if the outstanding update is older then X days; default: 1
  * `crit_days`: critical if the outstanding update is older then X days; default: 14
  * `ignore_rc`: ignore release candidate versions; default: True
  * `fetch_changelog_days`: fetch new changelogs once X day(s); default: 1
  * `fetch_changelog_timeout`: fetch changelog timeout in seconds; default: 20
  * `pkg_update_test`: perform a pkg update test; if set to `False`, the `PACKAGES` will be skipped; default: True
  * `pkg_update_timeout`: timeout for pkg update test in seconds; default: 20

### package audit

Audit installed packages against known vulnerabilities.

Sample output:
```
PKGAUDIT OK - no unacknowledged vulnerable packages found
```

You can acknowledge some package vulnerabilties using a `pkg_audit.yml` file; this can be distributed by defining
```
opn_check_mk_additional_files:
  pkg_audit.yml: "{{ opn_check_mk_lib_dir }}/local/"
```
A sample `pkg_audit.yml` can be generated using:
```
# /usr/local/lib/check_mk_agent/local/pkg_audit.py -p
---
curl:
  issues:
    - curl -- multiple vulnerabilities
...
```

### pfctl status
Check for problems in the current **pf** rule definitions;

Sample output:
```
PFCTLSTATUS - OK - pfctl rules OK
```

### check powerunit

Check power unit state using dmidecode (one check per unit).

Sample output:
```
0 PowerUnitGroup1 - OK - Power Unit Group: 1 Status: Present, OK
0 PowerUnitGroup2 - OK - Power Unit Group: 2 Status: Present, OK
```

## Role Variables

[defaults/main.yml](defaults/main.yml)

## Setup

### Check_MK Agent

The role can download the **Check_MK Agent for FreeBSD** from your checkmk server instance (see `checkmk_hostname`, `checkmk_path` and `checkmk_proto` in [defaults/main.yml](defaults/main.yml))

or you can download it on your own from
  * your check_mk instance (https://yourCheckMK/check_mk/wato.py?folder=&mode=download_agents)
  * or https://raw.githubusercontent.com/tribe29/checkmk/master/agents/check_mk_agent.freebsd

to `files/check_mk_agent.freebsd`.

### opnsense-facts

The role requires to be run after https://github.com/Rosa-Luxemburgstiftung-Berlin/ansible-opnsense-facts .

### Notes

The role must be run as root or w/ `become: true`.

And, of course, you will need to create a packet filter rule to allow connections from your checkmk server to the opnsense firewall on port 6556.

### Sample Playbook

```yaml
- name: opnsense
  hosts: opnsense
  vars:
    ansible_become: false
  roles:
    - role: ansible-opnsense-facts
      tags:
        - opnsense
        - facts
    - role: ansible-opnsense-checkmk
      tags:
        - opnsense
        - checkmk
```
