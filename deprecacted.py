#!/usr/bin/python

from passlib.hash import lmhash
import hashlib
import sys, time

#Check the hashed password against the provided wordlist
def check_hash(argv):
    in_file = sys.argv[1]
    hash_str = sys.argv[2]
    start = time.time()
    i = 0
    sz = file_len(in_file) 
    print'[*] Passwords in list: %d' % sz
    with open(in_file) as f:    
        for line in f:
            sys.stdout.write("\r[*] Hashes checked: %d" % i)
            sys.stdout.flush()
                
            line = line.rstrip('\n')
            if hashlib.md5(line).hexdigest() == hash_str:
                print'\n[>] md5 hashed password found: ' + line
                print '[*] Elapsed time: %s seconds' % (time.time() - start) + '\n'
                sys.exit(0)
            elif hashlib.sha224(line).hexdigest() == hash_str:
                print'\n[>] sha224 hashed password found: ' + line
                print'[*] Elapsed time: %s seconds' % (time.time() - start) + '\n'
                sys.exit(0) 
            elif hashlib.sha384(line).hexdigest() == hash_str:
                print'\n[>] sha384 hashed password found: ' + line
                print'[*] Elapsed time: %s seconds' % (time.time() - start) + '\n'
                sys.exit(0)
            elif hashlib.sha512(line).hexdigest() == hash_str:
                print'\n[>] sha512 hashed password found: ' + line
                print'[*] Elapsed time: %s seconds' % (time.time() - start) + '\n'
                sys.exit(0)
            elif hashlib.sha1(line).hexdigest() == hash_str:
                print'\n[>] sha1 hashed password found: ' + line
                print '[*] Elapsed time: %s seconds' % (time.time() - start) + '\n'
                sys.exit()
            elif hashlib.sha256(line).hexdigest() == hash_str:
                print'\n[>] sha256 hashed password found: ' + line
                print '[*] Elapsed time: %s seconds' % (time.time() - start) + '\n'
                sys.exit(0)
            elif lmhash.hash(line) == hash_str:
                print'\n[>] LM hashed password found: ' + line
                print '[*] Elapsed time: %s seconds' % (time.time() - start) + '\n'
                sys.exit(0)
            i += 1
        
    print'\n[x] No passwords found!'
    print'[*] Goodbye!'
        
    sys.exit(0)
 
#Get the number of lines in the wordlist    
def file_len(in_file):
    with open(in_file) as f:
        for i, l in enumerate(f):
            pass
    return i + 1
  
#Define script usage
def usage():
    print '\n[x] Usage:\thash_compare.py <path to wordlist> <hashed string>\n'
    print'Script will run <hashed string> against the contents of <wordlist> by checking every line in the file'
    print'using md5, sha1, sha224, sha256, sha384, sha512, and LM hashing algorithms.  If a match is found, the'
    print'the "unhashed" plaintext password and hash algorithm will be presented.\n\n'
    print'To hash string from terminal use echo with -n flag and pipe to desired hash\n'
    print'\tEX: echo -n qwerty | md5sum\n'
    sys.exit(0)
   
#Script entry 
if __name__ == "__main__":
    if len(sys.argv) != 3:
        usage()
        sys.exit(1)
        
    print'\n[*] Depending on the size of the wordlist, this may take several minutes...'
    time.sleep(1)
    try:
        check_hash(sys.argv[1:])
    except IOError:
        print '[x] "' + sys.argv[1] + '" not found!  Check the path and try again.'
        print'[x] Get your life together!\n'
        sys.exit(2)
    
    
    
