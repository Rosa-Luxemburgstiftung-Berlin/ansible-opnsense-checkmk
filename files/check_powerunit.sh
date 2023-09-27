#! /usr/bin/env bash

dmidecode -t 39 | grep -e 'Power Unit Group:\|Status:' | sed 'N;s/\n/ --- /;' | sed 's/\t//g' | while read PULine ; do
    PU=${PULine// --- *};
    PUcheck=$(echo $PU | sed 's/[ :]//g'); 
    PUStatus=${PULine//*, };
    ECODE=0;
    STATUS="OK"
    if [ "$PUStatus" != "OK" ]; then
        ECODE=2;
        STATUS="ERROR";
    fi
    PULine=$(echo $PULine | sed 's/ --- / /g')
    echo "$ECODE $PUcheck - $STATUS - $PULine" 
done
