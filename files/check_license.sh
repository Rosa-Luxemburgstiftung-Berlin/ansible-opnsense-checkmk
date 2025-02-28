#!/usr/local/bin/bash
# File to check
declare -r LICENSE_FILE="/usr/local/opnsense/version/core.license"

# Function to output error messages and exit
function error_exit {
    local message="$1"
    echo "$message"
    exit 3
}

# Ensure the file exists
if [[ ! -f "$LICENSE_FILE" ]]; then
    # no license file means community edition
    exit
fi

# Extract "valid_to" from the license file
VALID_TO=$(jq -r .valid_to "$LICENSE_FILE")
if [[ -z "$VALID_TO" ]]; then
    error_exit "3 LicenseCheck - UNKNOWN: 'valid_to' field not found or empty in $LICENSE_FILE"
fi

# Validate the format of the "valid_to" date
if ! date -j -f "%Y-%m-%d" "$VALID_TO" +%s >/dev/null 2>&1; then
    error_exit "3 LicenseCheck - UNKNOWN: Invalid date format for 'valid_to' in $LICENSE_FILE. Expected YYYY-MM-DD."
fi

# Convert dates to seconds since epoch
CURRENT_DATE=$(date +%s)
VALID_TO_EPOCH=$(date -j -f "%Y-%m-%d" "$VALID_TO" +%s)

# Ensure VALID_TO_EPOCH is a valid number
if [[ -z "$VALID_TO_EPOCH" || ! "$VALID_TO_EPOCH" =~ ^[0-9]+$ ]]; then
    error_exit "3 LicenseCheck - UNKNOWN: Unable to parse 'valid_to' as a valid date."
fi

# Calculate the days remaining
DAYS_REMAINING=$(( (VALID_TO_EPOCH - CURRENT_DATE) / 86400 ))

# Determine the status based on days remaining
if [[ $DAYS_REMAINING -lt 0 ]]; then
    echo "2 LicenseCheck - CRITICAL: License expired on $VALID_TO ($(( -DAYS_REMAINING )) days ago)"
    exit 2
elif [[ $DAYS_REMAINING -le 60 ]]; then
    echo "1 LicenseCheck - WARNING: License expires in $DAYS_REMAINING days on $VALID_TO"
    exit 1
else
    echo "0 LicenseCheck - OK: License is valid until $VALID_TO ($DAYS_REMAINING days remaining)"
    exit 0
fi
