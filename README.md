# ansible-opnsense-checkmk
ansible role for opnsense installing check_mk agent

## setup
define vars
```yaml
opn_packages:
  - bash
  - ipmitool
  - libstatgrab

opn_install_check_mk: True
```
The role must be run as root or w/ `become: yes`

## update
you may like to replace the `files/check_mk_agent.freebsd` with the **Check_MK Agent for FreeBSD** from your check_mk instance (https://yourCheckMK/check_mk/wato.py?folder=&mode=download_agents)
