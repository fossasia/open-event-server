#!/bin/bash
lines=`flask db heads | grep -c "head"`
if [ $lines -ne 1 ]
then
    echo "Error: Multiple Migration Heads"
	exit 1
else
	exit 0
fi

