#!/bin/bash
input_file="$1"
log_type=$(cat tmp/logtype.txt)

>"visualizations/times.csv"


gawk -v type="$log_type" -F, '
BEGIN {
    if (type == "android"){
    FS="!";
    OFS="!";
    }
    else{
    OFS = ","
    }
    
    split("Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec", months, " ")
    for (i=1; i<=12; i++) month_map[months[i]] = i
    curr_year = strftime("%Y")

}
NR == 1 {
    print $0, "epoch" >> "visualizations/times.csv"
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
        OFS="!";
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
    } 
    else {
    print "please have mercy"
    }
    gsub(/\r/, " ", $0)
    print $0,epoch >> "visualizations/times.csv"
}' "$input_file"
