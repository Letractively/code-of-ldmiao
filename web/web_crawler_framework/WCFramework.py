#!/usr/bin/python
# -*- coding: utf-8 -*-


import re
import urllib
import urllib2
import os
import sys
import random
import time

import codecs
import traceback

from threadpool import ThreadPool



#--------------------------------------------------------------------------------------
#Configuraion

host = 'http://songtaste.com'

#proxy = {'http': 'http://beiwebcache1.core.hp.com:8080'}
proxy = None

thread_count = 5


#--------------------------------------------------------------------------------------

#get the HTML Source from url through proxies
def getContent(url, proxies = None):
    '''
    if proxies==None:
        print "           -> Get:["+url+"]"
    else:
        print "           -> Get:["+url+"] through " + proxies['http']
    '''
    content = None
    test_time = 3
    #success = False
    #while(success == False):
    while(test_time>0):
        try:
            filehandle = None
            if proxies==None:
                filehandle = urllib.urlopen(url)
            else:
                filehandle = urllib.urlopen(url, proxies=proxies)
            content = filehandle.read()
            #print content
            #success = True
            test_time = 0
        except:
            #success = False
            test_time = test_time-1
            print "           -> Get:["+url+"] failed, " + str(test_time) + " times left~"
            time.sleep(random.randrange(8,12,1))
    return content

def existFile(filename):
    if os.path.exists(filename):
        return True
    else:
        return False