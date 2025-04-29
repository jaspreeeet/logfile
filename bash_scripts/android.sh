#!/bin/bash
FILE=$1
CSV=$2

# Ensure input file exists
if [ ! -f "$FILE" ]; then
    echo "Input file $FILE does not exist."
    exit 1
fi

# create the CSV with headers
echo "Line Id!Time!PID!TID!Level!Component!Content" > "$CSV"
ANDROID_REGEX='^[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{3} [0-9]+ [0-9]+ [A-Z] [A-Za-z]+: .*$'

regex="^([0-9]{2}-[0-9]{2}[ ]+[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{3})[[:space:]]*([0-9]+)[[:space:]]*([0-9]+)[[:space:]]*([A-Z])[[:space:]]*([A-Za-z]+): (.*)$"
# process the log file with sed, then add line numbers using nl and append to CSV
sed -E "s/$regex/\1!\2!\3!\4!\5!\6/" "$FILE" | nl -w 1 -s '!' >> "$CSV"