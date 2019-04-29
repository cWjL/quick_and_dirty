#!/usr/bin/env python

from threading import Thread
from passlib.hash import lmhash
import hashlib, argparse, sys
from itertools import islice

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--threads', action='store', dest='threads',help="Max threads. Default 20")
    reqd = parser.add_argument_group('required arguments')
    reqd.add_argument('-w','--wordlist',action='store',dest='list',help='Path to wordlist',required=True)
    reqd.add_argument('-p','--hashed',action='store',dest='hash',help='Hashed string',required=True)
    args = parser.parse_args()

    workers = []
    root = []
    div = 0
    #https://stackoverflow.com/a/2081880/4678883
    with open(args.list) as lst:
        root = lst.readlines()
        
    if args.threads is None:
        div = len(root)/20
        for i in range(20):
            tmp = []
            for i in range(div):
                tmp.append(root.pop(0))
            workers.append(Worker(tmp, args.hash))
    else:
        div = len(root)/20
        for i in range(20):
            tmp = []
            for i in range(div):
                tmp.append(root.pop(0))
            workers.append(Worker(tmp, args.hash))

    if len(root) > 0:
        workers.append(Worker(root, args.hash))
    print(len(workers))
    
if __name__ == "__main__":
    main()

class Worker(Thread):

    def __init__(self, list, hash):
        Thread.__init__(self)
        self.words = list
        self.target = hash

    def run(self):
        tmp = 0

