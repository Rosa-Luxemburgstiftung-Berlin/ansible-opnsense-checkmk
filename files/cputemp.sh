#!/usr/local/bin/bash

declare temp_warn=60
declare temp_crit=80

# Function to display temperatures for all found sensors of a specific type
display_temps() {
    local sensor_pattern=$1

    # Collect all relevant sensor readings
    sysctl -a | grep -E "$sensor_pattern" | while read sensor_data; do
        local sensor_id=$(echo $sensor_data | awk '{print $1}')
        local temp=$(echo $sensor_data | awk '{print $2}' | sed 's/C//')  # Removing 'C' from '44.0C'
        local temp_int=$(echo "$temp" | awk '{printf "%.0f", $1}')
        local ECODE=0
        local TXT="CPU Temp normal"

        # Determine status based on temperature thresholds
        if (( $(echo "$temp >= $temp_crit" | bc -l) )); then
            ECODE=2
            TXT="CPU Temp critical"
        elif (( $(echo "$temp >= $temp_warn" | bc -l) )); then
            ECODE=1
            TXT="CPU Temp warning"
        fi
        echo "$ECODE CPUTEMP-$sensor_id - temperature is $temp°C - $TXT"
    done
}
# Main script execution to check different sensor types
# Check AMD temperature sensors
if sysctl -a | grep -q 'dev.amdtemp.0.core0.sensor0'; then
    display_temps 'dev.amdtemp.[0-9]+.core[0-1].sensor[0-1]'
# Check Intel CPU temperature sensors
elif sysctl -a | grep -q 'dev.cpu.0.temperature'; then
    display_temps 'dev.cpu.[0-9]+.temperature'
# Check PCH temperature sensors, if any
elif sysctl -a | grep -q 'dev.pchtherm.0.temperature'; then
    display_temps 'dev.pchtherm.[0-9]+.temperature'
else
    echo "3 CPUTEMP - UNKNOWN - No thermal sensors found or active"
fi
