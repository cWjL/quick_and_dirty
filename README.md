# passwd_games


Script to check a hashed string against either a wordlist or a custom wordlist, as fast as possible.<br />

Will spawn as many processes as there are processor cores on the system on which it's run.<br />

Currently supports md5, sha224, sha384, sha512, sha1, sha256, LM, and Base64 encoded strings.<br /> 

**Install**

```git clone https://github.com/cWjL/passwd_games.git```<br />
```cd passwd_games```<br />
```pip install -r requirements.txt```<br />
```chmod +x passwd_games.py```<br />

**Platform**

&nbsp;```python 3```

**Custom Wordlist Config File**

The custom wordlist option uses a configuration file, ```trans.conf```, located in the root installation directory, to build the list. The first several lines of ```trans.conf``` describes it's usage.

**Usage**
```
usage: passwd_games.py [-h] [-w LIST] [-s HASH] [-c]

optional arguments:
  -h, --help            show this help message and exit
  -w LIST, --wordlist LIST
                        Path to wordlist
  -s HASH, --hash-string HASH
                        Hashed string
  -c, --custom          Create custom list from [CONF]
```

**Example**

Run against md5 hashed string "String" using rockyou.txt wordlist:<br />
```./passwd_games.py -w ~/wordlists/rockyou.txt -s fd8ef8f17659355d2358200baa5f8cdc```<br /><br />
Run against md5 hashed string "String" using custom wordlist:<br />
```./passwd_games.py -s fd8ef8f17659355d2358200baa5f8cdc -c```<br /><br />
Run against md5 hashed string "String" with custom wordlist prepended to rockyou.txt:<br />
```./passwd_games.py -w ~/wordlists/rockyou.txt -s fd8ef8f17659355d2358200baa5f8cdc -c```<br />
