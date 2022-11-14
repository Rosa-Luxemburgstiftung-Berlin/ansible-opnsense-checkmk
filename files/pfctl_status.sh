#! /usr/local/bin/bash

declare -i ECODE=0
declare STATUS="OK"
declare TXT=""
declare -r TMPFILE=$(mktemp -q -t pfctl_status)

if [ -f "$TMPFILE" ]; then
	pfctl -g -n -f /tmp/rules.debug 2>$TMPFILE
	declare -ri PFCTL=$?
	if [ $PFCTL = 0 ]; then
		TXT="pfctl rules OK"
	else
		STATUS="CRITICAL"
		ECODE=2
		TXT="pfctl error $PFCTL :"
		while read line; do
			lineno=$(echo $line | sed 's/:/ /g' | awk '{print $2}')
			eline=$(sed -n "${lineno}p" /tmp/rules.debug)
			TXT="$TXT $line $eline (!!)"
		done <$TMPFILE
	fi
else
	STATUS="UNKNOWN"
	ECODE=3
	TXT="error creating temp file"
fi

echo "$ECODE PFCTLSTATUS - $STATUS - $TXT" 
exit 0
