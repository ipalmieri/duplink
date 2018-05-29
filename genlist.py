#!/bin/python

import hashlib
import argparse
import sys
import os
import filecmp
import shlex

output_filename = "linklist.out"
output_fileobj = None
global_separator = " "

###########################################################
# File attributes
class fileInfo():
    def __init__(self):
        self.path = ""
        self.hash = ""
        #self.inode = ""
        #self.mtime = 0
        self.stat = None

    def __repr__(self):
        return str(self.__dict__)


###########################################################
# Delete old file, and hard-link to source
def dedup_file(source, target):
    global global_separator
    # Just write to output file
    output_fileobj.write(shlex.quote(source.path) + global_separator \
        + shlex.quote(target.path) + "\n") 
    return True


###########################################################
# Dedup files based on source table
def dedup_all(tpath, r_table):
    print("Deduping files on " + tpath)
    f_count = 0
    f_dedup = 0
    f_dsize = 0
    for cur_dir, chidl_dirs, files in os.walk(tpath):
        for f in files:
            f_count = f_count + 1
            f_target = fileInfo()
            f_target.path = os.path.join(cur_dir, f)
            f_target.stat = os.lstat(f_target.path)
            hobj = hashlib.sha256()
            with open(f_target.path, 'rb') as f_pl:
                hobj.update(f_pl.read())
            f_target.hash = hobj.hexdigest()
            # Hash test
            if f_target.hash in r_table:
                f_entry = r_table[f_target.hash]
                # Check if not already hard linked
                if not os.path.samefile(f_entry.path, f_target.path):
                    # Check if content is the same, collision proof
                    if filecmp.cmp(f_entry.path, f_target.path, False):
                        # Check if source is older than target
                        if f_entry.stat.st_mtime <= f_target.stat.st_mtime:
                           # Check if dedup of file was successful
                            if dedup_file(f_entry, f_target):
                                f_dedup = f_dedup + 1
                                f_dsize = f_dsize + f_target.stat.st_size
                        else:             
                                print(f_target.path + " is older than source file " + \
                                    f_entry.path + " please check them manually")
    print(str(f_count) + " file(s) scanned")
    print(str(f_dedup) + " file(s) marked to be deduped")
    print("Potential saving: " + str(f_dsize) + " bytes")


###########################################################
# Scans source tree gathering info
def scan_source(path):
    print("Scanning source in " + path)
    r_table = {}
    f_count = 0
    for cur_dir, child_dirs, files in os.walk(path):
        for f in files:
            f_count = f_count + 1
            f_entry = fileInfo()
            f_entry.path = os.path.join(cur_dir, f)
            # Tests to exclude uwanted file types
            if os.path.islink(f_entry.path):
                continue
            if os.path.getsize(f_entry.path) == 0:
                continue
            #f_entry.mtime = os.path.getmtime(f_entry.path)
            f_entry.stat = os.lstat(f_entry.path)
            hobj = hashlib.sha256() 
            with open(f_entry.path, 'rb') as f_pl:
                hobj.update(f_pl.read())
            f_entry.hash = hobj.hexdigest()
            #print(f_entry.path + " " + f_entry.hash)
            if f_entry.hash in r_table:
                f_old = r_table[f_entry.hash]
                if not filecmp.cmp(f_entry.path, f_old.path, False):
                    print("Colision of files " + f_entry.path 
                        + " and " + f_old.path)
                else:    
                    if (f_entry.stat.st_mtime < f_old.stat.st_mtime):
                        r_table[f_entry.hash] = f_entry
            else:
                r_table[f_entry.hash] = f_entry
    print(str(f_count) + " file(s) scanned")            
    return r_table


###########################################################
# Executes main algorithm
def dedupl(origin, target):
    if not os.path.isdir(origin):
        print(origin + " is not a valid folder path")
        return 1
    if not os.path.isdir(target):
        print(target + " is not a valid folder path")
        return 1
    r_table = scan_source(origin)
    #print(r_table)
    dedup_all(target, r_table)
    return 0

    
###########################################################
# main function
def main():
    global output_filename
    global output_fileobj
    parser = argparse.ArgumentParser(description='Hard-link duplicate files')
    parser.add_argument("source", help="Reference folder path")
    parser.add_argument("target", nargs='?', help="Folder to be deduped")
    args = parser.parse_args()
    dsrc = args.source
    dtrg = args.target
    if not dtrg:
        dtrg = dsrc
        print("Deduplicating files inside folder " + dsrc)
    else:
        print("Hard-linking files in " + dtrg + " to " + dsrc)
    
    try:
        output_fileobj = open(output_filename, 'w')
    except Exception as e:
        print("Error opening output file: " + str(e))
        sys.exit(1)
    else:    
        ret = dedupl(dsrc, dtrg)
        output_fileobj.close()
        sys.exit(ret)


###########################################################
# main function caller
if __name__ == "__main__":
    main()

