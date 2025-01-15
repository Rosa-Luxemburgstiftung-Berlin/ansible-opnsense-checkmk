#!/usr/local/bin/bash
# Define variables
declare -r VERSION=$(openvpn --version 2>/dev/null | head -n 1 | cut -d' ' -f1-3)
declare -i OPENVPN_PORT=${OPENVPN_PORT:-1194}
declare -r OPENVPN_STATUS=$(pluginctl -s openvpn status 2>&1)
declare -ri ECODE=$?

# Function to check active connections
check_connections() {
    if command -v netstat > /dev/null; then
	CONNECTIONS=$(netstat -an 2>/dev/null | grep -E "ESTABLISHED" | grep ":${OPENVPN_PORT}" | wc -l)
    else
        echo "Error: netstat command is not available on this system."
        exit 1
    fi
    echo "$CONNECTIONS"
}

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
    CONNECTIONS=$(check_connections)
    if [ $? -eq 0 ]; then
        echo "0 OpenVPN_Status - OpenVPN is running. Active connections: $CONNECTIONS, Version: $VERSION"
    else
        echo "1 OpenVPN_Status - OpenVPN is running, but failed to retrieve active connections."
        exit 1
    fi
else
    echo "2 OpenVPN_Status - OpenVPN is not running!"
    exit 2
fi
