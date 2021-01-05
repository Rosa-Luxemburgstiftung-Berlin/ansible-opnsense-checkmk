# ansible-opnsense-checkmk
ansible role for opnsense installing check_mk agent

## setup
Download the **Check_MK Agent for FreeBSD** from your check_mk instance (https://yourCheckMK/check_mk/wato.py?folder=&mode=download_agents) to `files/check_mk_agent.freebsd`.

The role must be run as root or w/ `become: yes`.
