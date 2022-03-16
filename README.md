[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](http://www.gnu.org/licenses/gpl-3.0)
[![lint](https://github.com/Rosa-Luxemburgstiftung-Berlin/ansible-opnsense-checkmk/actions/workflows/lint.yml/badge.svg)](https://github.com/Rosa-Luxemburgstiftung-Berlin/ansible-opnsense-checkmk/actions?query=workflow%3Aansible-lint)
[![pylint](https://github.com/Rosa-Luxemburgstiftung-Berlin/ansible-opnsense-checkmk/actions/workflows/pylint.yml/badge.svg)](https://github.com/Rosa-Luxemburgstiftung-Berlin/ansible-opnsense-checkmk/actions?query=workflow%3Apylint)

# ansible-opnsense-checkmk

Ansible role installing [check_mk](https://checkmk.com/) agent on [opnsense](https://opnsense.org/).

It includes some local checks:

  * gateway status monitoring
  * crash detection
  * firmware update status

## Role Variables

[defaults/main.yml](defaults/main.yml)

## Setup

### Check_MK Agent

Download the **Check_MK Agent for FreeBSD** from
  * your check_mk instance (https://yourCheckMK/check_mk/wato.py?folder=&mode=download_agents)
  * or https://raw.githubusercontent.com/tribe29/checkmk/master/agents/check_mk_agent.freebsd
to `files/check_mk_agent.freebsd`.

### opnsense-facts

The role requires to be run after https://github.com/Rosa-Luxemburgstiftung-Berlin/ansible-opnsense-facts .

### Notes

The role must be run as root or w/ `become: true`.

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
