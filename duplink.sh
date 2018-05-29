#!/bin/bash


# =======================================================================
# Configuration and environment variables 


# =======================================================================
# Main dedup loop
# $1 = link list filename
start_dedup()
{
        for i in "${INSTANCES[@]}"; do

                if [ "$1" == "$i" ]; then

                        if [ -d $BASEDIR/$1 ]; then

                                return
                        fi
                fi
        done

        exit 1
}

# =======================================================================
# Prints help
help() {
	echo Dedup files, creating hard links from a previously generated list 
	echo Use: 
	echo	$0 "<link list file>"
    exit 1
}


# =======================================================================
## Options parsing

if [[ $# -eq 1 ]] ; then

    if [[ -f "$1" ]] ; then
        start_dedup $1 
    elif [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]] ; then
        help
    else
        echo "$1 is not a valid file"
        help
    fi
else
	help
fi

