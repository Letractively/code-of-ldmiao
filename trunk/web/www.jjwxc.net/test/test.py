#!/usr/bin/python
# -*- coding:  gb2312-*-
import re

novelurls = open('novelurls.txt').read()
print novelurls
pattern = re.compile(r"""(http://www.jjwxc.net/onebook.php\?novelid=\d{1,}.*?)\n""", re.IGNORECASE| re.DOTALL| re.LOCALE| re.UNICODE)
novelurls = pattern.findall(novelurls)

for novelurl in novelurls:
	print novelurl, 'dddd'