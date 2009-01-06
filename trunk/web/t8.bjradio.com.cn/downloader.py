#!/usr/bin/env python
# -*- coding: utf-8 -*-


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

host = 'http://t8.bjradio.com.cn'

#proxy = {'http': 'http://beiwebcache1.core.hp.com:8080'}
proxy = {'http': 'http://web-proxy.hpl.hp.com:8088'}

proxy = None

pool = None
thread_count = 2

work_path = 'E:\\audio'

downloaded_video_set = None

#--------------------------------------------------------------------------------------
def getThreadPool():
    global pool
    if pool is None:
        pool = ThreadPool(thread_count)
    return pool
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
        f = open(work_path+'\\video_ids.txt', 'r')
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
        f = open(work_path+'\\video_ids.txt', 'w')
        for url in downloaded_video_set:
            f.write(url+'\n')
            f.flush()
        f.close()

def hasBeenDownloadedBeforeByVideoPageURL(url):
    global downloaded_video_set
    initDownloadedVideoIDSet()
    video_id = url.strip()
    if video_id in downloaded_video_set:
        return True
    else:
        return False

def hasBeenDownloadedBefore(video_url):
    global downloaded_video_set
    initDownloadedVideoIDSet()
    if video_url in downloaded_video_set:
        return True
    else:
        return False

def addToDownloadedVideoIDSet(video_url):
    global downloaded_video_set
    initDownloadedVideoIDSet()
    video_url = video_url.strip()
    if video_url and video_url !='':
        downloaded_video_set.add(video_url)
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
        log_file = open(work_path+'\\log.txt', 'a')
        log_file.write('[%s] %s\n'%( time.strftime('%Y-%m-%d %H:%M:%S'), str))
        log_file.flush()
        log_file.close()
    except:
        pass

def clearLog():
    global work_path
    log_file_path = work_path+'\\log.txt'
    if os.path.isfile(log_file_path):
        os.remove(log_file_path)

#--------------------------------------------------------------------------------------
def getVideoInfo(url):
    global proxy, host
    video_webpage = getContent(url, None, proxy)
    
    video_real_url = ''
    mobj = re.search(r'player.play\("(.*?)"\);', video_webpage)
    if mobj is None:
        return None
    else:
        video_real_url = mobj.group(1)

    # title
    video_title = ''
    mobj = re.search(r'<em>作品名：(.*?)</em>', video_webpage)
    if mobj is not None:
        video_title = mobj.group(1).decode('utf-8')

    return video_real_url, video_title

def downloadVideo(url):
    global proxy, work_path

    if hasBeenDownloadedBeforeByVideoPageURL(url):
        print "  Video:[" + url+ "] has been downloaded before, pass.\n"
        log("  Video:[" + url+ "] has been downloaded before, pass.\n")
        return

    video_real_url, video_title = getVideoInfo(url)
    video_file_type = video_real_url[video_real_url.rfind('.'):]
    
    saveFile(work_path+'\\audio', '%s%s'%(video_title, video_file_type), video_real_url);

def downloadAllVideos(url):
    global proxy, host, thread_count, pool
    pool = getThreadPool()
    
    htmlcontent = getContent(url, None, proxy)

    urlSet = set()
    
    matched_groups = re.findall(r'<a href="(/play\?id=\d+)".*?title=".*?"', htmlcontent)
    for matched in matched_groups:
        video_url = "%s%s"%(host, matched.strip())
        if video_url not in urlSet:
            urlSet.add(video_url)
            print video_url
            log(video_url)
            pool.queueTask(downloadVideo, (video_url))

def downloadVideosFromUID(uid, page_count):
    global pool
    pool = None
    pool = getThreadPool()
    for i in range(page_count):
        downloadAllVideos('http://t8.bjradio.com.cn/list?uid=%d&special_id=0&sort_by=0&p=%d'%(uid, i+1))
    pool.joinAll()

def downloadVideosWithKeyword(keyword, page_count):
    global pool
    pool = None
    pool = getThreadPool()
    for i in range(page_count):
        downloadAllVideos('http://t8.bjradio.com.cn/search?keyword=%s&p=%d'%(urllib.quote_plus(keyword), i+1))
    pool.joinAll()

    
#--------------------------------------------------------------------------------------
if __name__ == '__main__':
    clearLog()
    #url = 'http://t8.bjradio.com.cn/play?id=70942'
    #print getVideoInfo(url)
    #downloadVideo(url)
    
    #url = 'http://t8.bjradio.com.cn/list?p=2&uid=84215&special_id=0&sort_by=0'
    #downloadAllVideos(url)
    
    #downloadVideosWithKeyword('飞舞芳邻', 5)
    #downloadVideosWithKeyword('结婚进行曲', 3)
    #downloadVideosWithKeyword('婚姻诊所', 3)
    #downloadVideosWithKeyword('沉浮-灵与肉', 3)
    #downloadVideosWithKeyword('东坡', 3)
    #downloadVideosWithKeyword('唐宋才子的真实生活', 5)
    #downloadVideosWithKeyword('左手曾国藩右手胡雪岩', 4)
    #downloadVideosWithKeyword('我们仨', 3)
    #downloadVideosWithKeyword('清朝那些事儿', 5)
    #downloadVideosWithKeyword('明朝那些事', 26)
    
    #downloadVideosWithKeyword('大房地产商', 1)
    #downloadVideosWithKeyword('少年维特的烦恼', 1)
    #downloadVideosWithKeyword('谢谢你曾经爱过我', 5)
    #downloadVideosWithKeyword('崇祯王朝', 9)
    #downloadVideosWithKeyword('婚姻诊所', 3)
    
    downloadVideosFromUID(95322, 7)
    downloadVideosFromUID(84051, 24)
    downloadVideosFromUID(84631, 25)
    downloadVideosFromUID(84111, 38)
    downloadVideosFromUID(84215, 85)
    downloadVideosFromUID(84080, 480)
