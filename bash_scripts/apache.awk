BEGIN {
    FS = ",";
    print "Line Id,Day,Time,Level,Content,Event,Template" > "tmp.csv";
    E1 = "jk2_init() Found child <*> in scoreboard slot <*>";
    E2 = "workerEnv.init() ok <*>";
    E3 = "mod_jk child workerEnv in error state <*>";
    E4 = "[client <*>] Directory index forbidden by rule: <*>";
    E5 = "jk2_init() Can't find child <*> in scoreboard";
    E6 = "mod_jk child init <*> <*>";
    OFS = ",";
}
{gsub("\r","",$0)
        gsub("\n","",$0)}
/jk2_init\(\) Found child [^ ]* in scoreboard slot [^ ]*/ {
    print $0, "E1", E1 >> "tmp.csv";
    next;
}

/workerEnv\.init\(\) ok [^ ]*/ {
    print $0, "E2", E2 >> "tmp.csv";
    next;
}

/mod_jk child workerEnv in error state [^ ]*/ {
    print $0, "E3", E3 >> "tmp.csv";
    next;
}

/\[client [^ ]*\] Directory index forbidden by rule: [^ ]*/ {
    print $0, "E4", E4 >> "tmp.csv";
    next;
}

/jk2_init\(\) Can't find child [^ ]* in scoreboard/ {
    print $0, "E5", E5 >> "tmp.csv";
    next;
}

/mod_jk child init [^ ]*/ {
    print $0, "E6", E6 >> "tmp.csv";
    next;
}

NR>1{
    print $0, "-", "-" >> "tmp.csv";
}