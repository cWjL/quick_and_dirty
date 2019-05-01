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
from itertools import islice

res_queue = Queue()

def main():
    '''
    Entry main
    '''
    parser = argparse.ArgumentParser()
    reqd = parser.add_argument_group('required arguments')
    parser.add_argument('-w','--wordlist',action='store',dest='list',help='Path to wordlist')
    parser.add_argument('-s','--hash-string',action='store',dest='hash',help='Hashed string')
    parser.add_argument('-c','--custom', action='store',dest='conf',help='Create custom list from [CONF]')
    parser.add_argument('-r','--run-custom', action='store_true',dest='run',help='Run custom list')
    parser.add_argument('-f','--save-custom',action='store',dest='save',help='Save custom list as [FILE]')
    
    args = parser.parse_args()

    try:
        import colorama
        from colorama import Fore, Style
        colorama.init()
        b_prefix = "["+Fore.RED+"FAIL"+Style.RESET_ALL+"] "
        g_prefix = "["+Fore.GREEN+" OK "+Style.RESET_ALL+"] "
        n_prefix = "["+Fore.YELLOW+" ** "+Style.RESET_ALL+"] "
        rolling_1 = "["+Fore.GREEN+"*   "+Style.RESET_ALL+"] "
        rolling_2 = "["+Fore.YELLOW+" *  "+Style.RESET_ALL+"] "
        rolling_3 = "["+Fore.RED+"  * "+Style.RESET_ALL+"] "
        rolling_4 = "["+Fore.BLUE+"   *"+Style.RESET_ALL+"] "
    except ImportError:
        b_prefix = "[FAIL] "
        g_prefix = "[ OK ] "
        n_prefix = "[ ** ] "
        rolling_1 = "[*   ] "
        rolling_2 = "[ *  ] "
        rolling_3 = "[  * ] "
        rolling_4 = "[   *] "

    prefixes = [b_prefix, g_prefix,
                n_prefix, rolling_1,
                rolling_2, rolling_3,
                rolling_4]

    if not args.list and not args.hash and not args.cust:
        print(b_refix+"You didn't supply any arguments")
        parser.print_help()
        sys.exit(0)
    elif args.list and not args.hash:
        print(b_refix+"You need to supply a hashed string as an argument")
        parser.print_help()
        sys.exit(0)
    elif args.conf and not (args.run or args.save):
        print(b_refix+"You must supply either \'-r\' or \'-f\' with this option")
        parser.print_help()
        sys.exit(0)

    if args.list and args.hash:
        found = _check_hash(args.list, args.hash, prefixes)
    elif args.list and args.hash and args.conf:
        
        
    if found is not None:
        print(g_prefix+"Password found: "+found[1]+":"+found[0])
    else:
        print(b_prefix+"No password found")
        
    sys.exit(0)

def _create_custom(config):
    '''
    Create custom wordlist based on rules defined in <config>

    @param config file path
    @return list of custom passwords
    '''
    tmp = 0
    

def _check_hash(word_list, hashed, prefixes):
    '''
    Divide up word list by the number of available processor cores.
    Launch multiple processes to dictionary attack hashed string.

    @param path to wordlist
    @param hashed string to test
    @param list of prefixes
    @return found password (if found), None otherwise
    '''

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

    workers.append(Process(target=_wait_deco, args=(prefixes, )))

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

def _prepend(fp, custom, prefixes):
    '''
    Add elements in <custom> list to file pointed to by <fp>

    @param file pointer 
    @param list of words to add
    @param list of prefixes
    @return file path of new file
    '''
    if "win" in sys.platform:
        file_name = fp[fp.rfind('\\')+1:]
        file_path = fp[:fp.rfind('\\')+1]
    elif "linux" in sys.platform:
        file_name = fp[fp.rfind('/')+1:]
        file_path = fp[:fp.rfind('/')+1]

    print(prefixex[2]+"Copying new passwords to wordlist")
    with open(fp) as old:
        with open(file_path+"new_"+file_name, "w") as new:
            for nl in custom:
                new.write(nl+'\n')
            for line in old:
                new.write(line)
                
    print(prefixex[1]+"Copy done. New file: "+file_path+"new_"+file_name)

    return file_path+"new_"+file_name
            
            

def _div_list(fp, begin, end):
    '''
    Divide text file into list with size defined by begin and end

    @param file pointer
    @param begin integer index
    @param end integer index
    @return selected section of input file
    '''
    list_sec = []
    with open(fp, 'r', encoding=('latin-1')) as txt_file:
        for line in islice(txt_file, begin, end):
            list_sec.append(line)
    return list_sec

def _wait_deco(prefixes):
    '''
    Print wait decoration while active

    @param list of prefixes
    @return none
    '''
    i = 3
    while True:
        if not res_queue.empty():
            break
        if i % 7 == 0:
            i = 3
        print(prefixes[i], end='\r')
        i += 1
        time.sleep(.5)
    

class Worker(Thread):
    '''
    Multiprocessing worker thread
    '''

    def __init__(self, list, hash):
        '''
        Worker constructor

        @param list of words to check
        @param hashed string to test
        @return none
        '''
        Thread.__init__(self)
        self.words = list
        self.target = hash

    def run(self):
        '''
        Worker thread

        @param none
        @return none
        '''
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
    
