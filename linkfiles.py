#!/bin/python

import argparse
import sys
import os
import shlex

g_extension = "dedup00"

###########################################################
# Delete old file, and hard-link to source
def dedup_file(source, target):
    global g_extension
    tmp_target = target + "." + g_extension
    print("Linking " + target + " to " + source)
    if os.path.isfile(source) and os.path.isfile(target):
        try:
            os.rename(target, tmp_target)
        except Exception as e:
            print("Cannot move target file: " + str(e))
            return False
        try:
            os.link(source, target)
        except Exception as e:
            print("Cannot create hard link: " + str(e))
            os.rename(tmp_target, target)
            return False
        try:
            os.remove(tmp_target)
        except Exception as e:    
            print("Cannot remove " + tmp_target + ": " + str(e))
    else:
        print("One of the paths is not a file")
    return True


###########################################################
# Read link list and dedup files 
def dedup_list(filename):
    count_files = 0
    count_dedup = 0
    count_bytes = 0
    try:
        with open(filename, 'r') as f:
            for line in f:
                flist = shlex.split(line)
                if len(flist) != 2:
                    print("Error reading line: " + line)
                    continue
                count_files = count_files + 1    
                potential_save = os.path.getsize(flist[1])
                if not dedup_file(flist[0], flist[1]):
                    print("Error deduping pair : " + str(flist))
                    continue
                count_dedup = count_dedup + 1
                count_bytes = count_bytes + potential_save
    except Exception as e:
        print("Error opening input file: " + str(e))
        return 1
    print(str(count_files) + " file(s) read")
    print(str(count_dedup) + " file(s) deduped")
    print(str(count_bytes) + " byte(s) saved")
    return 0


###########################################################
# main function
def main():
    parser = argparse.ArgumentParser(description='Hard-link files from list')
    parser.add_argument("file", help="File containing link list")
    args = parser.parse_args()
    ifilename = args.file
    ret = dedup_list(ifilename)
    sys.exit(ret)


###########################################################
# main function caller
if __name__ == "__main__":
    main()

