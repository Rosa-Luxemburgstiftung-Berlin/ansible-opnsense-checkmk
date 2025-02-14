#!/usr/local/bin/bash
# Define variables
declare -r VERSION=$(openvpn --version 2>/dev/null | head -n 1 | cut -d' ' -f1-3)
declare -i OPENVPN_PORT=$(sed -nE 's/^port[[:space:]]+([0-9]+)$/\1/p' /var/etc/openvpn/*.conf)
declare -r OPENVPN_STATUS=$(pluginctl -s openvpn status 2>&1)
declare -ri ECODE=$?

# Function to check active connections
check_connections() {
    if command -v netstat > /dev/null; then
        connections=$(netstat -an 2>/dev/null | grep -E "ESTABLISHED" | grep -w ${OPENVPN_PORT} | wc -l | sed 's/^ *//')
    else
        echo "Error: netstat command is not available on this system."
        exit 1
    fi

    echo "$connections"
}

if [ -z "$OPENVPN_PORT" ] || [ "$OPENVPN_PORT" -eq 0 ]; then
    OPENVPN_PORT=1194
fi

# Check pluginctl command success
if [ $ECODE -gt 0 ]; then
    echo "3 OpenVPN_Status - OpenVPN status is undefined: $OPENVPN_STATUS"
    exit 3
fi

if [ -z "$OPENVPN_STATUS" ]; then
    # unconfigured, ergo check is not required
    exit 0
fi

# Check if OpenVPN is running
if echo "$OPENVPN_STATUS" | grep -q "is running"; then
    connections=$(check_connections)
    if [ $? -eq 0 ]; then
        echo "0 OpenVPN_Status - OpenVPN is running. Active connections: $connections, Version: $VERSION"
    else
        echo "1 OpenVPN_Status - OpenVPN is running, but failed to retrieve active connections."
        exit 1
    fi
else
    echo "2 OpenVPN_Status - OpenVPN is not running!"
    exit 2
fi
