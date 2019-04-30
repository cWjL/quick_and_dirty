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
    reqd.add_argument('-w','--wordlist',action='store',dest='list',help='Path to wordlist',required=True)
    reqd.add_argument('-p','--hashed',action='store',dest='hash',help='Hashed string',required=True)
    args = parser.parse_args()

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

    MAX_THREADS = multiprocessing.cpu_count()
    workers = []

    try:
        sz = sum(1 for i in open(args.list, 'rb'))
        print(n_prefix+"Wordlist length: "+str(sz))
    except IOError:
        print(b_prefix+"IOError")
        sys.exit(1)
       
    div = int(sz/MAX_THREADS)
    rem = sz - int(div*MAX_THREADS)
    incr = div
    i = 0
    print(n_prefix+"Using: "+str(MAX_THREADS)+" threads")
    print(n_prefix+"Words per thread: "+str(div)+" +/- "+str(rem))
    try:
        for turn in range(MAX_THREADS):
            print(n_prefix+"Getting section: "+str(turn), end='\r', flush=True)
            worker = Worker(_div_list(args.list, i, i+incr), args.hash)
            worker_p = Process(target=worker.run)
            workers.append(worker_p)
            #workers.append(Worker(_div_list(args.list, i, i+incr), args.hash))
            i += incr
        if rem > 0:
            print(g_prefix+"Getting last section")
            worker = Worker(_div_list(args.list, i, i+incr), args.hash)
            worker_p = Process(target=worker.run)
            workers.append(worker_p)
    except IOError:
        print(b_prefix+"IOError")

    print(n_prefix+"Created: "+str(len(workers))+" threads")
    print(g_prefix+"Starting threads")

    for worker in workers:
        worker.start()

    for worker in workers:
        worker.join()


    print(g_prefix+"All threads complete")
    if not res_queue.empty():
        queue_list = list(res_queue.get())
        print(g_prefix+"Password found: "+queue_list[1]+":"+queue_list[0])
    else:
        print(b_prefix+"No password found")
    
    sys.exit(0)

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
                    res_queue.put({'MD5',word})
                elif hashlib.sha224(word.encode('utf-8')).hexdigest() == self.target:
                    res_queue.put({'SHA224',word})
                elif hashlib.sha384(word.encode('utf-8')).hexdigest() == self.target:
                    res_queue.put({'SHA384',word})
                elif hashlib.sha512(word.encode('utf-8')).hexdigest() == self.target:
                    res_queue.put({'SHA512',word})
                elif hashlib.sha1(word.encode('utf-8')).hexdigest() == self.target:
                    res_queue.put({'SHA1',word})
                elif hashlib.sha256(word.encode('utf-8')).hexdigest() == self.target:
                    res_queue.put({'SHA256',word})
                elif lmhash.hash(word.encode('utf-8')) == self.target:
                    res_queue.put({'LM',word})
                elif base64.b64encode(word.encode('utf-8')) == self.target:
                    res_queue.put({'BASE64',word})
        
if __name__ == "__main__":
    main()
    
