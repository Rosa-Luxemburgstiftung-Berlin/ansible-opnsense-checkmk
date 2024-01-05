#! /usr/local/bin/bash

declare -i ECODE=0
declare STATUS="OK"
declare TXT=""

PCKCHECKDEPS="$(pkg check -d -a -n 2>&1 | sed '1d'; exit ${PIPESTATUS[0]})"
declare -ri PCKCHECKDEPSECODE=$?

if [ $PCKCHECKDEPSECODE -gt 0 ]; then
	STATUS="CRITICAL"
	ECODE=2
	TXT="pkg check exit code: $PCKCHECKDEPSECODE; output: $PCKCHECKDEPS"
elif [ -n "$PCKCHECKDEPS" ]; then
	STATUS="WARNING"
	ECODE=1
	TXT="$(echo $PCKCHECKDEPS)"
fi

echo "$ECODE PCK_CHECK_DEPENDENCIES - $STATUS - $TXT" 
exit 0
