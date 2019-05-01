#!/usr/bin/env python3
'''
Test speed against orig version with string: 0839236891
cat rockyou.txt | grep -n 0839236891
14344321: 0839236891
echo -n 0839236891 | md5sum
'''

from threading import Thread
import multiprocessing
from multiprocessing import Queue, Process
from passlib.hash import lmhash
import hashlib, argparse, sys
import base64, time
#from queue import Queue
from itertools import islice

res_queue = Queue()

def main():
    parser = argparse.ArgumentParser()
    reqd = parser.add_argument_group('required arguments')
    parser.add_argument('-w','--wordlist',action='store',dest='list',help='Path to wordlist')
    parser.add_argument('-hs','--hash_string',action='store',dest='hash',help='Hashed string')
    parser.add_argument('-c', '--custom', action='store',dest='cust',help='Create custom list')
    
    args = parser.parse_args()

    if not args.list and not args.hash and not args.cust:
        parser.print_help()
        sys.exit(0)

    try:
        import colorama
        from colorama import Fore, Style
        colorama.init()
        b_prefix = "["+Fore.RED+"FAIL"+Style.RESET_ALL+"] "
        g_prefix = "["+Fore.GREEN+" OK "+Style.RESET_ALL+"] "
        n_prefix = "["+Fore.YELLOW+" ** "+Style.RESET_ALL+"] "
    except ImportError:
        b_prefix = "[FAIL] "
        g_prefix = "[ OK ] "
        n_prefix = "[ ** ] "

    prefixes = [b_prefix, g_prefix, n_prefix]

    found = _check_hash(args.list, args.hash, prefixes)
    if found is not None:
        print(g_prefix+"Password found: "+found[1]+":"+found[0])
    else:
        print(b_prefix+"No password found")
        
    sys.exit(0)

def _check_hash(word_list, hashed, prefixes):

    MAX_THREADS = multiprocessing.cpu_count()
    workers = []

    try:
        sz = sum(1 for i in open(word_list, 'rb'))
        print(prefixes[2]+"Wordlist length: "+str(sz))
    except IOError:
        print(prefixes[0]+"IOError")
        sys.exit(1)
       
    div = int(sz/MAX_THREADS)
    rem = sz - int(div*MAX_THREADS)
    incr = div
    i = 0
    print(prefixes[2]+"Using: "+str(MAX_THREADS)+" cores")
    print(prefixes[2]+"Words per thread: "+str(div)+" +/- "+str(rem))
    try:
        for turn in range(MAX_THREADS):
            print(prefixes[2]+"Getting section: "+str(turn), end='\r', flush=True)
            worker = Worker(_div_list(word_list, i, i+incr), hashed)
            worker_p = Process(target=worker.run)
            workers.append(worker_p)
            i += incr
        if rem > 0:
            print(prefixes[2]+"Getting last section")
            worker = Worker(_div_list(word_list, i, i+incr), hashed)
            worker_p = Process(target=worker.run)
            workers.append(worker_p)
    except IOError:
        print(prefixes[0]+"IOError")

    print(prefixes[2]+"Created: "+str(len(workers))+" threads")

    for worker in workers:
        worker.start()

    print(prefixes[1]+"Threads started")

    for worker in workers:
        worker.join()

    print(prefixes[1]+"All threads complete")
    if not res_queue.empty():
        return res_queue.get()
    else:
        return None
    

def _div_list(fp, begin, end):
    list_sec = []
    with open(fp, 'r', encoding=('latin-1')) as txt_file:
        for line in islice(txt_file, begin, end):
            list_sec.append(line)
    return list_sec
    

class Worker(Thread):

    def __init__(self, list, hash):
        Thread.__init__(self)
        self.words = list
        self.target = hash

    def run(self):
        for word in self.words:
            word = word.rstrip('\n')
            if not res_queue.empty():
                break
            else:
                if hashlib.md5(word.encode('utf-8')).hexdigest() == self.target:
                    res_queue.put(('MD5',str(word)))
                elif hashlib.sha224(word.encode('utf-8')).hexdigest() == self.target:
                    res_queue.put(('SHA224',str(word)))
                elif hashlib.sha384(word.encode('utf-8')).hexdigest() == self.target:
                    res_queue.put(('SHA384',str(word)))
                elif hashlib.sha512(word.encode('utf-8')).hexdigest() == self.target:
                    res_queue.put(('SHA512',str(word)))
                elif hashlib.sha1(word.encode('utf-8')).hexdigest() == self.target:
                    res_queue.put(('SHA1',str(word)))
                elif hashlib.sha256(word.encode('utf-8')).hexdigest() == self.target:
                    res_queue.put(('SHA256',str(word)))
                elif lmhash.hash(word.encode('utf-8')) == self.target:
                    res_queue.put(('LM',str(word)))
                elif base64.b64encode(word.encode('utf-8')) == self.target:
                    res_queue.put(('BASE64',str(word)))
        
if __name__ == "__main__":
    main()
    
