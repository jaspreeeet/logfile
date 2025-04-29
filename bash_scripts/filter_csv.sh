#!/bin/bash

# Usage: bash_scripts/filter_csv.sh "2025-04-25T14:30" "2025-04-30T23:59" input.csv
start_time="$1"
end_time="$2"
input_file="$3"
output_file="$4"
log_type=$(cat tmp/logtype.txt)

# Portable epoch conversion function
datetime_to_epoch() {
    local dt="${1/T/ }"
    local pattern='^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}$'
    
    if [[ "$dt" =~ $pattern ]]; then
        if date --version >/dev/null 2>&1; then
            date -d "$dt" +%s 2>/dev/null
        else
            date -j -f "%Y-%m-%d %H:%M:%S" "$dt" +%s 2>/dev/null
        fi
    else
        return 1
    fi
}


# Convert with error handling
start_epoch=$(datetime_to_epoch "$start_time") || { echo "Invalid start_time"; exit 1; }
end_epoch=$(datetime_to_epoch "$end_time") || { echo "Invalid end_time"; exit 1; }

gawk -v st="$start_epoch" -v et="$end_epoch" -v type="$log_type" -v datecol="$date_column" -F, '
BEGIN {
    if (type == "android"){
    FS="!";
    OFS="!";
    }
    OFS = ","
    split("Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec", months, " ")
    for (i=1; i<=12; i++) month_map[months[i]] = i
    curr_year = strftime("%Y")

}
NR == 1 {
    print $0
    next
}
{
    
    if (type == "apache") {
        date_str = $3
        # Format: Jul 16 11:01:00 2006
        if (match(date_str, /^([A-Za-z]+) ([0-9]{1,2}) ([0-9]{2}):([0-9]{2}):([0-9]{2}) ([0-9]{4})$/, arr)) {
            month = month_map[arr[1]]
            day = arr[2]
            hour = arr[3]
            min = arr[4]
            sec = arr[5]
            year = arr[6]
            epoch = mktime(year " " month " " day " " hour " " min " " sec)
        } else { epoch = "" }
    }
    else if (type == "android") {
        date_str = $2
        # Format: 05-16 04:53:00.786
        if (match(date_str, /^([0-9]{2})-([0-9]{2}) ([0-9]{2}):([0-9]{2}):([0-9]{2})/, arr)) {
            month = arr[1]
            day = arr[2]
            hour = arr[3]
            min = arr[4]
            sec = arr[5]
            year = curr_year
            epoch = mktime(year " " month " " day " " hour " " min " " sec)
        } else { epoch = "" }
    }
    else if (type == "syslog") {
        date_str = $2
        # Format: Jul 27 14:41:57 (no year)
        if (match(date_str, /^([A-Za-z]+)[ ]+([0-9]{1,2})[ ]+([0-9]{2}):([0-9]{2}):([0-9]{2})$/, arr)) {
            month = month_map[arr[1]]
            day = arr[2]
            hour = arr[3]
            min = arr[4]
            sec = arr[5]
            year = curr_year
            epoch = mktime(year " " month " " day " " hour " " min " " sec)
        } else { epoch = "" }
    } else {
    print "please have mercy"
    }

    if (epoch != "" && epoch >= st && epoch <= et) {
    gsub("\r","",$0)
        gsub("\n","",$0)
        print $0
    }
}' "$input_file" > "$output_file"

echo "Filtered data between $start_time and $end_time ➡️ $output_file"
