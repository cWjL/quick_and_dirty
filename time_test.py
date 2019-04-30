#!/usr/bin/env python3
import os
from datetime import datetime

prefix = "[*] "
test_1 = "./quick_hash.py rockyou.txt f5dee0e0b7fdec0646e0dbededb7bb79"
test_2 = "./test.py -w rockyou.txt -p f5dee0e0b7fdec0646e0dbededb7bb79"
print(prefix+"Test Case 1:  Full file traversal")
print(prefix+"Starting "+test_1)
start_1 = datetime.now()
os.system(test_1)
elapsed_1 = datetime.now() - start_1

print(prefix+"Starting "+test_2)
start_2 = datetime.now()
os.system(test_2)
elapsed_2 = datetime.now() - start_2

print(prefix+"Test Complete\n\n")
print(prefix+"Results of: "+test_1)
print(prefix+"Test_1 time elapsed (hh:mm:ss.ms) {}".format(elapsed_1))
print(prefix+"Results of: "+test_2)
print(prefix+"Test_2 time elapsed (hh:mm:ss.ms) {}".format(elapsed_2))
