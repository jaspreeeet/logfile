#!/bin/bash
FILE=$1
CSV=$2

# ensure input file exists
if [ ! -f "$FILE" ]; then
    echo "Input file $FILE does not exist."
    exit 1
fi

# create the CSV with headers
echo "Line Id,Time,Level,Component,PID,Content" > "$CSV"


SYSLOG_REGEX='^[A-Z][a-z]{2} [0-9]{1,2} [0-9]{2}:[0-9]{2}:[0-9]{2}[[:space:]]*[a-z]+[[:space:]]*[a-z()]+\[[0-9]+\]: .*$'

regex='^([A-Z][a-z]{2})[ ]+([0-9]{1,2})[ ]+([0-9]{2}:[0-9]{2}:[0-9]{2})[ ]+([a-zA-Z0-9-]+)[[:space:]]+([a-zA-Z0-9_()/-]+)?\[([0-9]+)\]?:[[:space:]]*(.*)$'
# process the log file with sed, then add line numbers using nl and append to CSV
sed -E -n \
-e 's/^([A-Za-z]{3} [ 0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}) ([a-zA-z ]+) ([a-zA-z().0-9\-_]+)?\[([0-9]+)\]?: (.*)/\1,\2,\3,\4,\5/p' \
-e 's/^([A-Za-z]{3} [ 0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}) ([a-zA-z]+) ([^ :]+): (.*)/\1,\2,\3,-,\4/p
' "$FILE" | nl -w 1 -s ',' >> "$CSV"
