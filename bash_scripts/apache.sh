#!/bin/bash
FILE=$1
CSV=$2

# Ensure input file exists
if [ ! -f "$FILE" ]; then
    echo "Input file $FILE does not exist."
    exit 1
fi

# create the CSV with headers
echo "Line Id,Day,Time,Level,Content,Event,Template" > "$CSV"


regex="^\[([A-Z][a-z]{2}) (.+)\] \[([a-zA-Z]+)\] (.*)"
# process the log file with sed, then add line numbers using nl and append to CSV
sed -E "s/$regex/\1,\2,\3,\4/" "$FILE" | nl -w 1 -s ',' >> "$CSV"

# process the CSV file with awk to match patterns
$(awk -f bash_scripts/apache.awk "$CSV")


$(mv tmp.csv $CSV)
$(rm tmp.csv)