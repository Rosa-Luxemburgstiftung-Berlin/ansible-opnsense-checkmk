#!/usr/local/bin/bash
# Enhanced OpenVPN monitoring script for multiple instances with connection check

# Function to check active connections on a given port
check_connections() {
    local port="$1"
    if command -v netstat >/dev/null 2>&1; then
        # Count established connections on the specified port
        netstat -an 2>/dev/null | grep -E "ESTABLISHED" | grep -w "$port" | wc -l | sed 's/^ *//'
    else
        echo "Error: netstat command is not available on this system."
        exit 1
    fi
}

# Retrieve OpenVPN status using pluginctl
OpenVPN_STATUS=$(pluginctl -s openvpn status 2>&1)
if [ $? -ne 0 ]; then
    echo "3 OpenVPN_Status - OpenVPN status is undefined: $OpenVPN_STATUS"
    exit 3
fi

# Initialize exit code and message
declare -i EXITCODE=0
MSG=""

# Iterate over each OpenVPN configuration file
for file in $([ -d /var/etc/openvpn/ ] && find /var/etc/openvpn/ -type f   -name \*.conf); do
    # Extract the base name of the configuration file (without .conf)
    instance=$(basename "$file" .conf)

    # Determine the instance identifier based on file naming
    if [[ "$instance" == instance-* ]]; then
        # For instance-<UUID>.conf, extract the UUID
        identifier="${instance#instance-}"
    elif [[ "$instance" == server* ]]; then
        # For server<ID>.conf, extract the numeric ID (or keep as is)
        identifier="${instance#server}"
    else
        # Skip files that don't match expected patterns
        echo "Skipping unrecognized configuration file: $file"
        continue
    fi

    # Extract the port number from the configuration file.
    # Use "lport" for server configs and "port" for instance configs.
    if [[ "$instance" == server* ]]; then
        port=$(sed -nE 's/^[[:space:]]*lport[[:space:]]+([0-9]+).*$/\1/p' "$file")
    else
        port=$(sed -nE 's/^[[:space:]]*port[[:space:]]+([0-9]+).*$/\1/p' "$file")
    fi
    if [ -z "$port" ] || [ "$port" -eq 0 ]; then
        port=1194
    fi

    # Search for the status line for the current instance in the pluginctl output.
    status_line=$(echo "$OpenVPN_STATUS" | grep -E "^openvpn\[$identifier\]")

    if [ -n "$status_line" ]; then
        if echo "$status_line" | grep -q "is running"; then
            # If running, check active connections on the extracted port.
            connections=$(check_connections "$port")
            MSG+="0 OpenVPN_$identifier - $status_line on port $port. Active connections: $connections.\n"
        else
            MSG+="2 OpenVPN_$identifier - $status_line\n"
            EXITCODE=2
        fi
    else
        MSG+="2 OpenVPN_$identifier - Status not found.\n"
        EXITCODE=2
    fi
done

# Output the accumulated messages
echo -e "$MSG"

# Exit with the appropriate code
exit $EXITCODE
