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

import config
from config import ListPattern, DataPattern, ProcessPath
from threadpool import ThreadPool



#--------------------------------------------------------------------------------------
#Configuraion

host = 'http://songtaste.com'

#proxy = {'http': 'http://beiwebcache1.core.hp.com:8080'}
proxy = None

thread_count = 5


#--------------------------------------------------------------------------------------------------------------

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

#--------------------------------------------------------------------------------------------------------------
class Crawler:
    name = None
    startURL = None
    host = None
    pattern_dict = None
    path_list = None
    
    
    def __init__(self, name, startURL, pattern_dict, path_list):
        self.name = name
        self.startURL = startURL
        self.pattern_dict = pattern_dict
        self.path_list = path_list
        self.host = self.getHostFromURL(startURL)
    
    def getHostFromURL(self, url):
        if not url:
            return None
        if url.find('http://')==0:
            new_url = url[7:]
        
        return 'http://'+new_url[:new_url.find('/')]
    
    def getRealURL(self, url_pattern, matched):
        url = url_pattern.replace('%H', self.host)
        for i in range(len(matched)):
            #print i, matched[i]
            url = url.replace('%'+str(i+1), unicode(matched[i], 'utf-8', 'ignore'))
        
        return url
        
    def crawle(self):
        self.crawleFromURL(self.startURL)
        
    def crawleFromURL(self, url):
        global proxy
        
        for path in path_list:
            print path
            if re.search(path.URLPattern, url):
                for process_name in path.process_list:
                    process = pattern_dict[process_name];
                    if not process:
                        continue
                    
                    htmlcontent = getContent(url, proxy)
                    
                    if isinstance(process, ListPattern):
                        print process.subPattern, process.subURL
                        matched_groups = re.findall(process.subPattern, htmlcontent)
                        
                        for matched in matched_groups:
                            #print 'subURL:', matched
                            subURL = self.getRealURL(process.subURL, matched)
                            url = subURL
                            print 'subURL:', subURL
                        
                        if process.nextPagePattern and process.nextPageURL:
                            print process.nextPagePattern, process.nextPageURL
                            matched_groups = re.findall(process.nextPagePattern, htmlcontent)
                            for matched in matched_groups:
                                nextPageURL = self.getRealURL(process.nextPageURL, matched)
                                print 'nextPageURL:', nextPageURL
                            
                    elif isinstance(process, DataPattern):
                        print process.dataPattern, process.dataURL
                        matched_groups = re.findall(process.dataPattern, htmlcontent)
                        for matched in matched_groups:
                            #print 'dataURL:', matched
                            dataURL = self.getRealURL(process.dataURL, matched)
                            print 'dataURL:', dataURL
                            
                        
                break
                
#--------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    pattern_dict, path_list = config.getConfig('conf.xml')
    
    #pprint.pprint(pattern_dict)
    for i in pattern_dict.values():
        print i

    #pprint.pprint(path_list)
    for i in path_list:
        print i
        
        
    crawler = Crawler('user_recommendation', 'http://songtaste.com/user/36692/allrec', pattern_dict, path_list)
    crawler.crawle()
    