#!/bin/bash
# usage: $0 "/motherlessDir"
cd "$1"/by-id
for i in *; do if [ ${i:0:1} != "H" -a ! -e ../html/H$i ]; then wget -O ../html/H$i http://motherless.com/H$i; fi; done

# relative links to absolute links
cd "$1"
find ./ -type l -execdir bash -c 'ln -sfn "$(readlink -f "$0")" "$0"' {} \;

