#!/usr/local/bin/bash

declare -i ECODE=0
declare STATUS="OK"
declare TXT=""
declare temp_warn=60
declare temp_crit=80

# Read the temperature from sysctl
if sysctl -a | grep -q dev.amdtemp.0.core0.sensor0; then
    temp="$(sysctl -a | grep dev.amdtemp.0.core0.sensor0 | awk '{print $2}' | sed 's/.$//')"
    STATUS="$temp°C"
else
    # If no temperature is found
    STATUS="UNKNOWN"
    ECODE=3
    TXT="Cannot measure temperature"
fi

# Convert temperature to integer for comparison, if needed
temp_int=$(echo "$temp" | awk '{printf "%.0f", $1}')

# Debug output
echo "Temperature read: $temp_float"
echo "Warning threshold: $temp_warn"
echo "Critical threshold: $temp_crit"

# Use bc for floating-point comparisons
if (( $(echo "$temp >= $temp_crit" | bc -l) )); then
    ECODE=2
    TXT="CPU Temp critical"
elif (( $(echo "$temp >= $temp_warn" | bc -l) )); then
    ECODE=1
    TXT="CPU Temp warning"
else
    TXT="CPU Temp normal"
fi

# Output result and exit with appropriate code
echo "$ECODE CPUTEMP - $STATUS - $TXT"
exit $ECODE
