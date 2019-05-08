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
import base64, time, re, random
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
    parser.add_argument('-c','--custom', action='store_true',dest='conf',help='Create custom list from [CONF]')
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

    if not args.list and not args.hash and not args.conf:
        print(b_refix+"You didn't supply any arguments")
        parser.print_help()
        sys.exit(0)
    elif args.list and not args.hash:
        print(b_refix+"You need to supply a hashed string as an argument")
        parser.print_help()
        sys.exit(0)
    elif args.conf and not (args.run or args.save):
        try:
            trans = Transform()
            tmp = trans.gen_list()
        except IOError:
            print("Config file not found")
            sys.exit(1)
        ############## DEBUG ################################################################
        with open("debug.txt", "w+") as test:
            for item in tmp:
                test.write("{}\n".format(item))
        ####################################################################################
            
        #print(trans.gen_list())
        #print(b_refix+"You must supply either \'-r\' or \'-f\' with this option")
        #parser.print_help()
        sys.exit(0)

    if args.list and args.hash:
        found = _check_hash(args.list, args.hash, prefixes)
    elif args.list and args.hash and args.conf:
        #generate custom list, add it to args.list list and run it
        tmp = 0
        
        
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

class Transform(object):
    '''
    String transformations
    '''
    def __init__(self):
        '''
        Transform constructor

        @param list of words to transform
        '''
        try:
            with open("trans.conf","r") as conf:
                self.in_list = conf.readlines()
        except IOError as e:
            raise IOError("trans.conf not found")

    def gen_list(self):
        '''
        Return custom list

        @param none
        @return custom password list
        '''
        #return self._parse_config()
        inter_list = self._parse_config()
        return self._xform(inter_list)

    def get_config(self):
        '''
        Return config list

        @param none
        @reutrn stripped config list
        '''
        return self.in_list
    
    def _xform(self, inter_list):
        '''
        Generate custom list from config rules
        
        @param parsed config list
        @return custom list
        '''
        final_list = []
        for item in inter_list:

            if item.get('mods') is None:

                if isinstance(item.get('str'), list):
                    final_list.extend(self._mod_str(self._str_combine(item.get('str'))))
                else:
                    final_list.extend(self._mod_str(item.get('str').strip('\n')))
            else:
                
                if isinstance(item.get('str'), list):
                    #print("here")
                    final_list.extend(self._mod_str_combine(item.get('str'),item.get('mods')))

        return final_list

    def _mod_str(self, in_str):
        '''
        Mod string

        @param string
        @return modified string list
        '''
        final_list = []
        if isinstance(in_str, str):
            inter_list = []
            # build base strings
            inter_list.append(in_str)
            inter_list.append(self._every_other_upper_leading(in_str))
            inter_list.append(self._every_other_upper_trailing(in_str))
            inter_list.append(self._leet(in_str))
            inter_list.append(self._first_letter_upper(in_str))
            final_list.extend(inter_list)
            # send list of base strings to remaining modifiers
            for item in inter_list:
                final_list.extend(self._add_nums(item))
                final_list.extend(self._spcl_chars(item))
                final_list.extend(self._spcl_chars(self._leet(item)))
                final_list.extend(self._spcl_chars(self._first_letter_upper(item)))
                final_list.extend(self._spcl_chars(self._every_other_upper_leading(item)))
                final_list.extend(self._spcl_chars(self._every_other_upper_trailing(item)))
                final_list.extend(self._spcl_chars_lst(self._add_nums(item)))

            if " " in in_str:
                no_space = self._no_spaces(in_str)
                inter_list = []
                # build base strings
                inter_list.append(no_space)
                inter_list.append(self._every_other_upper_leading(no_space))
                inter_list.append(self._every_other_upper_trailing(no_space))
                inter_list.append(self._leet(no_space))
                inter_list.append(self._first_letter_upper(no_space))
                final_list.extend(inter_list)
                # send list of base strings to remaining modifiers
                for item in inter_list:
                    final_list.extend(self._add_nums(item))
                    final_list.extend(self.spcl_chars(item))
                    final_list.extend(self.spcl_chars(self._every_other_upper_leading(item)))
                    final_list.extend(self.spcl_chars(self._every_other_upper_trailing(item)))
                    final_list.extend(self.spcl_chars(self._leet(item)))
                    final_list.extend(self.spcl_chars(self._first_letter_upper(item)))
                    final_list.extend(self.spcl_chars(self._add_nums(item)))
        elif isinstance(in_str, list):
            for item in in_str:
                inter_list = []
                # build base strings
                inter_list.append(item)
                inter_list.append(self._every_other_upper_leading(item))
                inter_list.append(self._every_other_upper_trailing(item))
                inter_list.append(self._leet(item))
                inter_list.append(self._first_letter_upper(item))
                final_list.extend(inter_list)
                # send list of base strings to remaining modifiers
                for word in inter_list:
                    final_list.extend(self._add_nums(word))
                    final_list.extend(self._spcl_chars(word))
                    final_list.extend(self._spcl_chars(self._leet(word)))
                    final_list.extend(self._spcl_chars(self._first_letter_upper(word)))
                    final_list.extend(self._spcl_chars(self._every_other_upper_leading(word)))
                    final_list.extend(self._spcl_chars(self._every_other_upper_trailing(word)))
                    final_list.extend(self._spcl_chars_lst(self._add_nums(word)))

                if " " in in_str:
                    no_space = self._no_spaces(in_str)
                    inter_list = []
                    inter_list.append(no_space)
                    inter_list.append(self._every_other_upper_leading(no_space))
                    inter_list.append(self._every_other_upper_trailing(no_space))
                    inter_list.append(self._leet(no_space))
                    inter_list.append(self._first_letter_upper(no_space))
                    final_list.extend(inter_list)
                    for word in inter_list:
                        final_list.extend(self._add_nums(word))
                        final_list.extend(self.spcl_chars(word))
                        final_list.extend(self.spcl_chars(self._every_other_upper_leading(word)))
                        final_list.extend(self.spcl_chars(self._every_other_upper_trailing(word)))
                        final_list.extend(self.spcl_chars(self._leet(word)))
                        final_list.extend(self.spcl_chars(self._first_letter_upper(word)))
                        final_list.extend(self.spcl_chars(self._add_nums(word)))

        return final_list

    def _mod_str_combine(self, in_str, in_mod_lst):
        '''
        Combine strings with modifiers

        @param string list
        @param string modifier list
        @return combined string list
        '''
        final_list = []
        '''
        Using max memory in _append_to

        essentially crashes host
        '''
        def _append_to(in_lst, in_str):
            final_list = list(in_lst)
            for item in in_lst:
                final_list.append(item+in_str)
            return final_list

        def _mod(in_str):
            '''
            Modify this to include the following
            EX INPUT: 1/25/1996
            EX OUTPUT: 1996, 96, jan 25 1996, 25 jan 1996
            '''
            final_list = []
            int_to_str = {
                0:"zero",1:"one",2:"two",3:"three",4:"four",
                5:"five",6:"six",7:"seven",8:"eight",9:"nine",
                10:"ten",11:"eleven",12:"twelve",13:"thirteen",
                14:"fourteen",15:"fifteen",16:"sixteen",17:"seventeen",
                18:"eighteen",19:"nineteen",20:"twenty",21:"twentyone",
                22:"twentytwo",23:"twentythree",24:"twentyfour",25:"twentyfive",
                26:"twentysix",27:"twentyseven",28:"twentyeight",29:"twentynine",
                30:"thirty",31:"thirtyone"
            }
            date_dd_mm_yyyy_sl = re.compile('.*/.*/.*')
            date_dd_mm_yyyy_ds = re.compile('.*-.*-.*')
            year = re.compile('.{4}')
            date_words = ""
            if date_dd_mm_yyyy_sl.match(in_mod_lst) or date_dd_mm_yyyy_ds.match(in_mod_lst):
                date_lst = []
                if date_dd_mm_yyyy_sl.match(in_mod_lst):
                    date_lst = in_mod_lst.split('/')
                elif date_dd_mm_yyyy_ds.match(in_mod_lst):
                    date_lst = in_mod_lst.split('-')
                print(date_lst)
                date_words += int_to_str.get(int(date_lst[0]))+" "
                date_words += int_to_str.get(int(date_lst[1]))+" "
                year = list(map(int, date_lst[2]))
                for digit in year:
                    date_words += int_to_str.get(digit)+" "
                # date should now be in the following format
                # EX: 01/12/1990
                #     one twelve one nine nine zero
                date_words.rstrip(" ")
            else:
                try:
                    year = list(map(int, in_str))
                    for digit in year:
                        date_words += int_to_str.get(digit)+" "
                    date_words.rstrip(" ")
                except:
                    date_words = in_str

            return date_words

        def _date_mod(in_str):
            
                
        if isinstance(in_str, list):
            final_list.extend(self._str_combine(in_str))
        else:
            final_list.append(in_str)
            
        if isinstance(in_mod_lst, str):
            final_list.extend(_append_to(final_list, _mod(in_mod_lst)))
        else:
            for item in in_mod_lst:
                final_list.extend(_append_to(final_list, _mod(item)))

        ##################################################################
        ############## DEBUG ############################################
        print(len(final_list))
        for item in final_list:
            print(item)
        sys.exit(0)
        #################################################################
        return final_list

    def _str_combine(self, in_lst):
        '''
        Combine strings in list is various ways

        @param string list
        @return combined string list
        '''
        final_list = []
        combiners = [
            "and",
            "or",
            "with"
        ]
        inter_list = []
        com_str = ""
        
        # combine names in in_lst order
        for item in in_lst:
            com_str += item+" "
            
        inter_list.append(com_str.rstrip(" "))
        com_str = ""

        # combine names in reverse in_lst order
        for item in reversed(in_lst):
            com_str += item+" "

        inter_list.append(com_str.rstrip(" "))

        # add combiners in between, in both fwd and rev orders
        for com in combiners:
            tmp = ""
            for item in in_lst:
                tmp += item +" "+com+" "
            tmp = tmp.rstrip(" ")
            inter_list.append(tmp.rstrip(com))
            tmp = ""
            for item in reversed(in_lst):
                tmp += item +" "+com+" "
            tmp = tmp.rstrip(" ")
            inter_list.append(tmp.rstrip(com))

        if len(in_lst) > 2:
            # shuffle list a few times
            for i in range(len(in_lst)):
                # create random order 1
                random.shuffle(in_lst)
                # combine names in in_lst order
                for item in in_lst:
                    com_str += item+" "
            
                inter_list.append(com_str.rstrip(" "))
                com_str = ""

                # combine names in reverse in_lst order
                for item in reversed(in_lst):
                    com_str += item+" "

                inter_list.append(com_str.rstrip(" "))

                # add combiners in between, in both fwd and rev orders
                for com in combiners:
                    tmp = ""
                    for item in in_lst:
                        tmp += item +" "+com+" "
                    inter_list.append(tmp.rstrip(" "))
                    tmp = ""
                    for item in reversed(in_lst):
                        tmp += item +" "+com+" "
                    inter_list.append(tmp.rstrip(" "))

        for item in inter_list:
            final_list.append(item)
            final_list.append(self._first_letter_upper(item))
            final_list.append(self._no_spaces(self._first_letter_upper(item)))
            final_list.append(self._no_spaces(item))

        return final_list

    def _parse_config(self):
        '''
        Parse config file

        @param none
        @return formatted list
        '''
        tmp = 0
        inter_list = []
        for item in self.in_list:
            if item is not '\n':
                item = item.rstrip()
                if '#' in item:
                    continue
                if ',' not in item and ':' not in item:
                    data = {'str':item.rstrip(),
                            'mods':None
                    }
                    inter_list.append(data)
                elif ',' in item and ':' not in item:
                    data = {'str':item.split(','),
                            'mods':None
                    }
                    inter_list.append(data)
                elif ':' in item:
                    data_break = item.split(':')
                    if ',' in data_break[0]:
                        str_data = data_break[0].split(',')
                    else:
                        str_data = data_break[0]

                    if ',' in data_break[1]:
                        mod_data = data_break[1].split(',')
                    else:
                        mod_data = data_break[1]
                    
                    data = {'str':str_data,
                            'mods':mod_data
                    }
                    inter_list.append(data)

        return inter_list

    def _spcl_chars_lst(self, in_lst):
        '''
        Add special characters to string

        @param string list
        @return string list with special characters appended
        '''
        final_list = []
        spcl_chars = ["!","@",
                      "#","$",
                      "%","^",
                      "&","*"
        ]
        for item in in_lst:
            for spcl in spcl_chars:
                final_list.append(item+spcl)
                final_list.append(spcl+item)

        return final_list

    def _spcl_chars(self, in_str):
        '''
        Add special characters to string

        @param string
        @return string list with special characters appended
        '''
        final_list = []
        spcl_chars = ["!","@",
                      "#","$",
                      "%","^",
                      "&","*",
                      "(",")"
        ]
        for spcl in spcl_chars:
            final_list.append(in_str+spcl)
            final_list.append(spcl+in_str)

        return final_list
        
    def _leet(self, in_str):
        '''
        Leetspeak generator
        
        @param non-leet string
        @return leet string
        '''
        leet = (
            (('o', 'O'), '0'),
            (('i', 'I'), '1'),
            (('e', 'E'), '3'),
            (('s', 'S'), '5'),
            (('a', 'A'), '4'),
            (('t', 'T'), '7'),
        )
        for origs, repl in leet:
            for orig in origs:
                in_str = in_str.replace(orig, repl)
        return in_str

    def _every_other_upper_leading(self, in_str):
        '''
        Capitalize every other letter of the given string beginning at index 0

        @param some string
        @return string with every other character capitalized
        '''
        capital = [False]
        def repl(some_str):
            capital[0] = not capital[0]
            return some_str.group(0).upper() if capital[0] else some_str.group(0).lower()
        return re.sub(r'[A-Za-z]', repl, in_str)

    def _every_other_upper_trailing(self, in_str):
        '''
        Capitalize every other letter of the given string beginning at index 1

        @param some string
        @return string with every other character capitalized
        '''
        capital = [False]
        def repl(some_str):
            capital[0] = not capital[0]
            return some_str.group(0).lower() if capital[0] else some_str.group(0).upper()
        return re.sub(r'[A-Za-z]', repl, in_str)

    def _first_letter_upper(self, in_str):
        '''
        Capitalize first letter of words in string

        @param some string
        @return string with first letter of all separate words upper case
        '''
        def repl(some_str):
            return some_str.group(1) + some_str.group(2).upper()
        return re.sub("(^|\s)(\S)", repl, in_str)

    def _no_spaces(self, in_str):
        '''
        Remove spaces between words

        @param some string
        @return string with spaces removed
        '''
        return in_str.replace(" ","")

    def _add_nums(self, in_str):
        '''
        Adds common password number formats to string

        @param some string
        @return list of new strings
        '''
        formatted = []
        #for item in in_lst:
        for i in range(0,10):
            formatted.append(in_str+str(i))

        for i in range(0,10):
            for j in range(0,10):
                formatted.append(in_str+str(i)+str(j))

        for i in range(0,10):
            for j in range(0,10):
                for k in range(0,10):
                    formatted.append(in_str+str(i)+str(j)+str(k))

        return formatted
        

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
    
