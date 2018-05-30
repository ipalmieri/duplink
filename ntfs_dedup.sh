#!/bin/sh

# This script automatically deduplicates NTFS filesystem trees 

# =======================================================================
# Configuration and environment variables 
LISTFILE="linklist.out"

# =======================================================================
# Main dedup loop
# $1 = device containing NTFS partition (e.g. /dev/sd0i)
# $2 = temporary mountpoint
# $3 = source folder relative to mountpoint
# $4 = (optional) target folder relative to mountpoint
start_dedup()
{
    device=$1
    mntpoint=$2
    # Mount volume using default driver
    echo "** Step 1: mount NTFS read-only"
    if mount | grep $mntpoint > /dev/null ; then
        echo "Error: $mntpoint is already mounted"
        exit 1
    fi    
    /sbin/mount -v -t ntfs $device $mntpoint
    if [[ $? -ne 0 ]] ; then
        echo "Error mounting $device"
        exit 1
    fi   
    # Check folders and run genlist
    echo "** Step 2: generate link list"
    sourcef=$2/$3
    if [[ $# -eq 3 ]] ; then
        python3 genlist.py $sourcef
    elif [[ $# -eq 4 ]] ; then
        targetf=$2/$4
        python3 genlist.py $sourcef $targetf 
    fi
    if [[ $? -ne 0 ]] ; then
        echo "Error running genlist"
        /sbin/umount $mntpoint
        exit 1
    fi    
    # Re-mount volume using ntfs-3g
    echo "** Step 3: umount NTFS and mount read-write ntfs-3g"
    /sbin/umount -v $mntpoint
    if [[ $? -ne 0 ]] ; then
        echo "Error umouting $mntpoint, aborted"
        exit 1
    fi
    if ! [[ -s $LISTFILE ]] ; then
        echo "No possible dedup to be done, exiting"
        exit 0
    fi    
    /usr/local/bin/ntfs-3g $device $mntpoint
    if [[ $? -ne 0 ]] ; then
        echo "Error mouting $mntpoint using ntfs-3g"
        exit 1
    fi    
    # Run linklist to dedup files
    echo "** Step 4: dedup files from list"
    python3 linkfiles.py $LISTFILE
    if [[ $? -ne 0 ]] ; then
        echo "Error deduping files"
        /sbin/umount $mntpoint
        exit 1
    fi
    /sbin/umount -v $mntpoint
    exit 0
}


# =======================================================================
# Prints help
help() 
{
    echo "Dedup files in a NTFS volume"
    echo "Use:" 
    echo "   $0 <device> <mountpoint> <folder>"
    echo "   $0 <device> <mountpoint> <source> <target>"
    echo "Folders are relative to mountpoint"
    exit 1
}


# =======================================================================
## Options parsing
if [[ $# -eq 3 ]] ; then
    start_dedup $1 $2 $3
elif [[ $# -eq 4 ]] ; then
    start_dedup $1 $2 $3 $4
else
	help
fi

