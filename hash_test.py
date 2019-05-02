#!/usr/bin/env python3
from passlib.hash import lmhash
import hashlib, argparse, sys, enchant
import base64, time, re, string
from nltk import everygrams

def main():
    passwd = sys.argv[1].rstrip('\n')
    hashpw = sys.argv[2]
    print(passwd)
    print(hashpw)

    if hashlib.md5(passwd.encode('utf-8')).hexdigest() == hashpw:
        print("md5")
    elif hashlib.sha224(passwd.encode('utf-8')).hexdigest() == hashpw:
        print("sha224")
    elif hashlib.sha384(passwd.encode('utf-8')).hexdigest() == hashpw:
        print("sha384")
    elif hashlib.sha512(passwd.encode('utf-8')).hexdigest() == hashpw:
        print("sha512")
    elif hashlib.sha1(passwd.encode('utf-8')).hexdigest() == hashpw:
        print("sha1")
    elif hashlib.sha256(passwd.encode('utf-8')).hexdigest() == hashpw:
        print("sha256")
    elif lmhash.hash(passwd.encode('utf-8')) == hashpw:
        print("lmhash")
    elif base64.b64encode(passwd.encode('utf-8')) == hashpw:
        print("base64")

def test_bed(fp):
    custom = ["kendall","kaydence","frank","otis"]
    if "win" in sys.platform:
        file_name = fp[fp.rfind('\\')+1:]
        file_path = fp[:fp.rfind('\\')+1]
    elif "linux" in sys.platform:
        file_name = fp[fp.rfind('/')+1:]
        file_path = fp[:fp.rfind('/')+1]

    with open(fp) as old:
        with open(file_path+"new_"+file_name, "w") as new:
            for nl in custom:
                new.write(nl+'\n')
            for line in old:
                new.write(line)

def _2_1337(non_1337):
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
            non_1337 = non_1337.replace(orig, repl)
    return non_1337

def every_other_upper(norm_str):
    capital = [False]
    def repl(some_str):
        capital[0] = not capital[0]
        return some_str.group(0).upper() if capital[0] else some_str.group(0).lower()
    return re.sub(r'[A-Za-z]', repl, norm_str)

def first_letter_upper(norm_str):
    def repl(some_str):
        return some_str.group(1) + some_str.group(2).upper()
    return re.sub("(^|\s)(\S)", repl, norm_str)

def check_words(data):
    '''
    Fucntion to parse given data for readable strings
 
    @param data: the data to be parsed
    @param alpha_list: characters that should be ignored as "words"
    @return: string if found, None otherwise
    '''

    two_letters = [
        "are", "of", "to", "in",
        "it", "is", "be", "as",
        "at", "so", "we", "he",
        "by", "or", "on", "do",
        "if", "me", "my", "up",
        "an", "go", "no", "us",
        "am"
    ]
    	
    three_letters = [
        "the", "and", "for", "are",
        "but", "not", "you", "all",
        "any", "can", "had", "her",
        "was", "one", "our", "out",
        "day", "get", "has", "him",
        "his", "how", "man", "new",
        "now", "old", "see", "two",
        "way", "who", "boy", "did",
        "its", "let", "put", "say",
        "she", "too", "use"
    ]

    	
    four_letters = [
        "that", "with", "have", "this",
        "will", "your", "from", "they",
        "know", "want", "been", "good",
        "much", "some", "time"
    ]

    dict = enchant.Dict("en_US")
    legit_words = []
    word_list = [''.join(_ngr) for _ngr in everygrams(data) if dict.check(''.join(_ngr)) and len(_ngr) > 1]
   
    for item in word_list:
        if len(item) == 2:
            if item in two_letters:
                legit_words.append(item)
        elif len(item) == 3:
            if item in three_letters:
                legit_words.append(item)
        elif len(item) == 4:
            if item in four_letters:
                legit_words.append(item)
        else:
            legit_words.append(item)
            
    return legit_words

if __name__ == "__main__":
    #main()
    #test_bed(sys.argv[1])
    #print(_2_1337(sys.argv[1]))
    #print(every_other_upper(sys.argv[1]))
    #print(first_letter_upper(sys.argv[1]))
    print(check_words(sys.argv[1]))

