#!/usr/bin/env python
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

import convert_flv

#--------------------------------------------------------------------------------------
#Configuraion

host = 'http://www.youtube.com'

#proxy = {'http': 'http://beiwebcache1.core.hp.com:8080'}
proxy = {'http': 'http://web-proxy.hpl.hp.com:8088'}

proxy = None

pool = None
thread_count = 5

work_path = 'D:\Develop\Others\code-of-ldmiao\web\youtube.com'

downloaded_video_set = None

#--------------------------------------------------------------------------------------

#get the HTML Source from url through proxies
def getContent(url, data=None, proxies=None):
    
    std_headers = {	
        'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.1) Gecko/2008070208 Firefox/3.0.1',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
        'Accept': 'text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5',
        'Accept-Language': 'en-us,en;q=0.5',
    }
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
            if data:
                data = urllib.urlencode(data)
            if proxies is not None:
                proxy_support = urllib2.ProxyHandler(proxies)
                opener = urllib2.build_opener(proxy_support)
                urllib2.install_opener(opener)
            
            request = urllib2.Request(url, data, std_headers)
            response = urllib2.urlopen(request)
            content = response.read()
            
            #print content
            #success = True
            test_time = 0
        except urllib2.HTTPError, e:
            print 'The server couldn\'t fulfill the request. Error code: ', e.code
            content = None
            break
        except urllib2.URLError, e:
            print 'We failed to reach the server. Reason: ', e.reason
            content = None
            break
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

#--------------------------------------------------------------------------------------
def initDownloadedVideoIDSet():
    global downloaded_video_set, work_path
    if downloaded_video_set is None:
        downloaded_video_set = set()
        f = open(work_path+'/video_ids.txt', 'r')
        line = f.readline()
        while line:
            line = line.strip()
            if line and line !='':
                downloaded_video_set.add(line)
            line = f.readline()
        f.close()
    return downloaded_video_set

def persistDownloadedVideoIDSet():
    global downloaded_video_set, work_path
    if downloaded_video_set is not None:
        f = open(work_path+'/video_ids.txt', 'w')
        for url in downloaded_video_set:
            f.write(url+'\n')
            f.flush()
        f.close()

def hasBeenDownloadedBeforeByVideoPageURL(url):
    global downloaded_video_set
    initDownloadedVideoIDSet()
    video_id = None
    mobj = re.search('''\\?v=(.*)''', url.strip())
    if mobj is not None:
        video_id = mobj.group(1)
        if video_id in downloaded_video_set:
            return True
    return False

def hasBeenDownloadedBefore(video_url):
    global downloaded_video_set
    initDownloadedVideoIDSet()
    video_id = None
    mobj = re.search('''video_id=(.*?)&t''', video_url)
    if mobj is not None:
        video_id = mobj.group(1)
        if video_id in downloaded_video_set:
            return True
    return False

def addToDownloadedVideoIDSet(video_url):
    global downloaded_video_set
    initDownloadedVideoIDSet()
    video_id = None
    mobj = re.search('''video_id=(.*?)&t''', video_url)
    if mobj is not None:
        video_id = mobj.group(1)
        if video_id and video_id !='':
            downloaded_video_set.add(video_id)
            persistDownloadedVideoIDSet()

#--------------------------------------------------------------------------------------
def saveFile(path, name, url):
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

    save_path = path+'\\'+name
    if existFile(save_path):
        print "  File:[" + save_path+ "] already exists, pass.\n"
        log("  File:[" + save_path+ "] already exists, pass.\n")
        addToDownloadedVideoIDSet(url)
        return
    
    print "  Downloading:[" + save_path+ "] ..."
    log("  Downloading:[" + save_path+ "] ...\n")
        
    global proxy
    content = getContent(url, None, proxy)
    if content:
        f = open(save_path,"wb")
        f.write(content)
        f.close()
        print " File   Saved:[" + save_path + "]"
        log(" URL Downloaded:[" + url + "]")
        addToDownloadedVideoIDSet(url)
    else:
        print " Failed   for:[" + save_path + "]"
        log(" Failed for:[" + url + "]")


def log(str):
    global work_path
    try:
        log_file = open(work_path+'\log.txt', 'a')
        log_file.write('[%s] %s\n'%( time.strftime('%Y-%m-%d %H:%M:%S'), str))
        log_file.flush()
        log_file.close()
    except:
        pass

def clearLog():
    global work_path
    log_file_path = work_path+'\log.txt'
    if os.path.isfile(log_file_path):
        os.remove(log_file_path)

#--------------------------------------------------------------------------------------
def getVideoInfo(url):
    global proxy, host
    video_webpage = getContent(url, None, proxy)

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

    if hasBeenDownloadedBeforeByVideoPageURL(url):
        print "  Video:[" + url+ "] has been downloaded before, pass.\n"
        log("  Video:[" + url+ "] has been downloaded before, pass.\n")
        return

    video_real_url, video_title, simple_title = getVideoInfo(url)
    saveFile(work_path+'\\youtube_videos', '%s.flv'%(video_title), video_real_url);

def downloadAllVideos(url):
    global proxy, host, thread_count, pool
    htmlcontent = getContent(url, None, proxy)

    video_url_set = set()
    matched_groups = re.findall('''"(/watch\\?v=.*?)"''', htmlcontent)
    for matched in matched_groups:
        video_url = "%s%s"%(host, matched.strip())
        video_url_set.add(video_url)

    for video_url in video_url_set:
        print video_url
        log(video_url)
        pool.queueTask(downloadVideo, (video_url))

def downloadSearchedVideo(search_words):
    global pool
    pool = ThreadPool(thread_count)

    for word in search_words:
        downloadAllVideos(search_video_url%(urllib.quote_plus(word)))

    pool.joinAll()

#--------------------------------------------------------------------------------------
if __name__ == '__main__':
    clearLog()
    #print getVideoInfo('http://www.youtube.com/watch?v=W8xfmFMz1RE')
    #downloadVideo('http://www.youtube.com/watch?v=W8xfmFMz1RE')
    search_video_url = 'http://www.youtube.com/results?search_query=%s&search_sort=video_date_uploaded&page=1'

    search_words = ['头脑风暴',
                    '锵锵三人行',
                    '文涛拍案',
                    '有报天天读',
                    '新闻今日谈',
                    '金石财经',
                    '时事开讲',
                    '文茜小妹大',
                    '文茜世界周报',
                    '中天骇客赵少康',
                    '文道非常道',
                    '世界周刊',
                    '新闻周刊',
                    ]
    downloadSearchedVideo(search_words)

    convert_flv.convertFlv2Mp4underDir(work_path+'\\youtube_videos')

