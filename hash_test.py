#!/usr/bin/env python3
from passlib.hash import lmhash
import hashlib, argparse, sys
import base64, time

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
