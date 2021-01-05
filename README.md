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
