#!/bin/bash

# Use command line arg over env variable
if [ ! -z "$BBB"  ] && [ $# -eq 0 ]
then
    addr=$BBB
elif [ ! -z "$1" ]
then
    addr=$1
# Check default BBB addresses
elif ping -c 1 -q -W1 192.168.7.2 &>/dev/null; then
  addr=192.168.7.2
elif ping -c 1 -q -W1 192.168.6.2  &>/dev/null; then
  addr=192.168.6.2 
else
    echo "export and set BBB or use ./reload.sh [IP]"
    exit
fi

dir="${PWD##*/}"
rsync -r -a --exclude=build/testing --exclude=scripts --exclude=venv --exclude=ghidra-pyi --delete ../$dir/ debian@$addr:/home/debian/$dir/
