#!/bin/bash

LOGFILE="$1"
CSV_OUT="$2"
TMP_LOGTYPE="tmp/logtype.txt"

# define regexes
APACHE_REGEX='^\[[A-Za-z]{3} [A-Za-z]{3} [0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2} [0-9]{4}\][ ]+\[[A-Za-z]+\][ ]*.*'
ANDROID_REGEX='^[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{3}[ ]*[0-9]+[ ]*[0-9]+[ ]*[A-Z][ ]*[A-Za-z]+: .*$'
SYSLOG_REGEX='^[A-Z][a-z]{2}[ ]+[0-9]{1,2}[ ]+[0-9]{2}:[0-9]{2}:[0-9]{2}[ ]+[^ ]+[ ]+[a-zA-Z0-9_. ()/-]+(\[[0-9]+\])?:[ ]*.+$'
# Sun Jul 16 11:01:00 2006          apache
# 05-16 04:53:00.786                android
# Jul 27 14:41:57                   syslog


# function: check if every line matches a regex
all_match() {
    local regex="$1"
    local file="$2"
    [ "$(grep -cEv "$regex" "$file")" -eq 0 ]
}

# detect log type
if all_match "$APACHE_REGEX" "$LOGFILE"; then
    echo "apache" > "$TMP_LOGTYPE"
    bash bash_scripts/apache.sh "$LOGFILE" "$CSV_OUT"

elif all_match "$ANDROID_REGEX" "$LOGFILE"; then
    echo "android" > "$TMP_LOGTYPE"
    bash bash_scripts/android.sh "$LOGFILE" "$CSV_OUT"

elif all_match "$SYSLOG_REGEX" "$LOGFILE"; then
    echo "syslog" > "$TMP_LOGTYPE"
    bash bash_scripts/syslog.sh "$LOGFILE" "$CSV_OUT"

else
    echo "none" > "$TMP_LOGTYPE"
    echo "⚠️ log type not recognized"
    exit 1
fi
