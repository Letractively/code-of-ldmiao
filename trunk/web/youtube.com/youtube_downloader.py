﻿#!/usr/bin/env python
# -*- coding: utf-8 -*-

#import youtube-dl as youtube


import re
import urllib
import urllib2
import os
import sys
import random
import time

import htmlentitydefs
import string

import codecs
import traceback

from threadpool import ThreadPool

#--------------------------------------------------------------------------------------
#Configuraion

host = 'http://www.youtube.com'

#proxy = {'http': 'http://beiwebcache1.core.hp.com:8080'}
proxy = {'http': 'http://web-proxy.hpl.hp.com:8088'}

proxy = None

thread_count = 5

work_path = 'D:\Develop\Others\code-of-ldmiao\web\youtube.com'

#--------------------------------------------------------------------------------------

#get the HTML Source from url through proxies
def getContent(url, proxies = None):
    '''
    if proxies==None:
        print "           -> Get:["+url+"]"
    else:
        print "           -> Get:["+url+"] through " + proxies['http']
    '''
    log("Get:["+url+"]")
    
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
            print "Get:["+url+"] failed, " + str(test_time) + " times left~"
            log("Get:["+url+"] failed, " + str(test_time) + " times left~")
            time.sleep(random.randrange(8,12,1))
    return content

def existFile(filename):
    if os.path.exists(filename):
        return True
    else:
        return False
    
def saveFile(path, name, content):
    #--------------------------------------------------------------------------
    #Replace all the invalid characters
    #re.sub('''[\\\\/\:\*\?"<>\|]+''', '-', '\\,/,|,",:,*,?,<,>')
    #re.sub('''[\\\\/\:\*\?"<>\|]+''', '-', '\\/|":*?<>')
    #Replace '\' and '/' to empty string ''
    name = re.sub('''[\\\\/]+''', '_', name)
    #Replace ':', '*', '?', '"', '<', '>', '|' to string '-'
    name = re.sub('''[\:\*\?"<>\|]+''', '-', name)
    name = name.strip()
    #--------------------------------------------------------------------------
    
    if not os.path.isdir(path):
        if existFile(path):
            print "  Path:["+ path+ "] is not a directory, exit!\n"
            log("  Path:["+ path+ "] is not a directory, exit!\n")
            return
        else:
            os.makedirs(path)
    
    save_path = path+'/'+name
    if existFile(save_path):
        print "  File:[" + save_path+ "] already exists, pass.\n"
        log("  File:[" + save_path+ "] already exists, pass.\n")
        return
        
    if content:
        f = open(save_path,"wb")
        f.write(content)
        f.close()
        print " File  Saved:[" + save_path + "]"
        log(" File  Saved:[" + save_path + "]")
    else:
        print " Failed  for:[" + save_path + "]"
        log(" Failed  for:[" + save_path + "]")
    
def log(str):
    global work_path
    log_file = open(work_path+'\log.txt', 'a')
    log_file.write('[%s] %s\n'%( time.strftime('%Y-%m-%d %H:%M:%S'), str))
    log_file.flush()
    log_file.close()
    
    
#--------------------------------------------------------------------------------------
def getVideoInfo(url):
    global proxy, host
    video_webpage = getContent(url, proxy)
    
    # Extract video id from URL
    video_id = ''
    VALID_URL = r'^((?:http://)?(?:\w+\.)?youtube\.com/(?:(?:v/)|(?:(?:watch(?:\.php)?)?\?(?:.+&)?v=)))?([0-9A-Za-z_-]+)(?(1).+)?$'
    mobj = re.match(VALID_URL, url)
    if mobj is None:
        return None
    else:
        video_id = mobj.group(2)

    t_param = ''
    mobj = re.search(r', "t": "([^"]+)"', video_webpage)
    if mobj is None:
        return None
    else:
        t_param = mobj.group(1)
    
    video_real_url = '%s/get_video?video_id=%s&t=%s' % (host, video_id, t_param)
    
    # title
    video_title = ''
    mobj = re.search(r'(?im)<title>YouTube - ([^<]*)</title>', video_webpage)
    if mobj is not None:
        video_title = mobj.group(1).decode('utf-8')
        video_title = re.sub(ur'(?u)&(.+?);', lambda x: unichr(htmlentitydefs.name2codepoint[x.group(1)]), video_title)
        video_title = video_title.replace(os.sep, u'%')

    # simplified title
    simple_title_chars = string.ascii_letters.decode('ascii') + string.digits.decode('ascii')
    simple_title = re.sub(ur'(?u)([^%s]+)' % simple_title_chars, ur'_', video_title)
    simple_title = simple_title.strip(ur'_')
    
    return video_real_url, video_title, simple_title

def downloadVideo(url):
    global proxy, work_path
    video_real_url, video_title, simple_title = getVideoInfo(url)
    
    content = getContent(video_real_url, proxy)
    saveFile(work_path+'\youtube_videos', '%s.flv'%(video_title), content);
    
def downloadAllVideos(url):
    global proxy, host, thread_count
    htmlcontent = getContent(url, proxy)
    
    pool = ThreadPool(thread_count)
    
    video_url_set = set()
    matched_groups = re.findall('''"(/watch\\?v=.*?)"''', htmlcontent)
    for matched in matched_groups:
        video_url = "%s%s"%(host, matched.strip())
        video_url_set.add(video_url)
    
    for video_url in video_url_set:
        print video_url
        log(video_url)
        pool.queueTask(downloadVideo, (video_url))
        
    pool.joinAll()
    
#--------------------------------------------------------------------------------------
if __name__ == '__main__':
    #print getVideoInfo('http://www.youtube.com/watch?v=W8xfmFMz1RE')
    #downloadVideo('http://www.youtube.com/watch?v=W8xfmFMz1RE')
    search_video_url = 'http://www.youtube.com/results?search_query=%s&search_sort=video_date_uploaded'
    #downloadAllVideos(search_video_url%(urllib.quote_plus('文茜小妹大')))
    downloadAllVideos(search_video_url%(urllib.quote_plus('文茜世界周报')))
    downloadAllVideos(search_video_url%(urllib.quote_plus('锵锵三人行')))
    downloadAllVideos(search_video_url%(urllib.quote_plus('文涛拍案')))
    downloadAllVideos(search_video_url%(urllib.quote_plus('中天骇客赵少康')))

