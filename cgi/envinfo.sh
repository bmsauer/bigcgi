#!/usr/local/bin/bash

echo "Content-Type: text/plain"
echo ""
echo ""
echo "Starting output of environment..." 1>&2
echo "OS:"
echo $(uname -mrs)
echo "Bash Interpreter:"
echo $(which bash)
echo "Python Interpreter:"
echo "/usr/local/bin/$(ls /usr/local/bin | grep ^python3..$)"
echo "/usr/local/bin/$(ls /usr/local/bin | grep ^python2..$)"
echo "TCL Interpreter:"
echo "/usr/local/bin/$(ls /usr/local/bin | grep ^tclsh...$)"
echo "Perl Interpreter:"
echo $(which perl)
echo "tcsh Interpreter:"
echo $(which tcsh)
echo "AWK Interpreter:"
echo $(which awk)
echo '------------------------------'
id
echo "Done output of environment..." 1>&2

