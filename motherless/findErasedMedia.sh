#!/bin/bash
# execute in motherless-dir/by-id/
echo The following files only exist on your local HD: >&2
echo >&2

for file in *; do
    id="`basename "$file"`"
    if wget --spider "http://motherless.com/$id" >>/dev/null 2>&1; then
        true
    else
        echo $file
    fi
done

