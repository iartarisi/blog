#!/usr/bin/env python

"""usage: pyblee [-s|--sitedir=SITEDIR] [-d|--datadir=DATADIR]

mumumu
"""

import sys
import os
import getopt

from blog import Blog
from post import Post

from config import DATADIR, SITEDIR 

def usage():
    print __doc__

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hd:s:", 
                ["help", "datadir=", "sitedir="])
    except getopt.GetoptError, err:
        usage()
        sys.exit(2)
    
    for opt, arg in opts:
        if opt in ('-h','--help'):
            usage()
            sys.exit()
        elif opt in ('-d','--datadir'):
            datadir = arg
        elif opt in ('-s','--sitedir'):
            SITEDIR = arg
        else:
            assert False, "unhandled option"

    blog = Blog()
    
    for a in args:
        if a == 'update':
            blog.update()
        elif a == 'archive':
            blog.archive()
    if args == []:
        blog.update_all()

if __name__ == '__main__':
    main()
