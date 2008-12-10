#!/usr/bin/env python
# -*- coding: utf-8 -*-


import re
import urllib
import urllib2
import os
import sys
import random
import time

from urllib2 import Request, urlopen, URLError, HTTPError

import htmlentitydefs
import string

import codecs
import traceback

from threadpool import ThreadPool

import convert_flv

#--------------------------------------------------------------------------------------
#Configuraion

host = 'http://v.youku.com'

get_flvurl_service_url = 'http://www.wbwb.net/video/'

#proxy = {'http': 'http://beiwebcache1.core.hp.com:8080'}
proxy = {'http': 'http://web-proxy.china.hp.com:8080'}

proxy = None

thread_count = 5

work_path = 'D:\\Develop\\Others\\code-of-ldmiao\\web\\youku.com'

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
    
    if proxies==None:
        print "           -> Get:["+url+"]"
    else:
        print "           -> Get:["+url+"] through " + proxies['http']
    

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
        except HTTPError, e:
            print 'The server couldn\'t fulfill the request.'
            print 'Error code: ', e.code
            content = None
            break
        except URLError, e:
            print 'We failed to reach a server.'
            print 'Reason: ', e.reason
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
    
    if url is not None:
        url = url.strip()
        if url in downloaded_video_set:
            return True
    return False

def hasBeenDownloadedBefore(video_id):
    global downloaded_video_set
    initDownloadedVideoIDSet()
    
    if url is not None:
        url = url.strip()
        if url in downloaded_video_set:
            return True
    return False

def addToDownloadedVideoIDSet(video_id):
    global downloaded_video_set
    initDownloadedVideoIDSet()
    if video_id and video_id !='':
        video_id = video_id.strip()
        downloaded_video_set.add(video_id)
        persistDownloadedVideoIDSet()

#--------------------------------------------------------------------------------------
def getAllFlvContent(url):
    global proxy
    
    all_content = None
    mobj = re.search(r'''(.*?/st/flv/fileid/\d{8})(\d{2})(.*)''', url)
    if mobj is not None:
        url_prefix = mobj.group(1)
        file_order = mobj.group(2)
        url_suffix = mobj.group(3)
        for i in range(10):
            url = url_prefix+'%02d'+url_suffix
            url = url%(i)
            print url
            content = getContent(url, None, proxy)
            if content is None:
                break
            if all_content is None:
                all_content = content
            else:
                all_content += content
    
    return all_content
    
def saveFile(path, name, url, video_id):
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
        addToDownloadedVideoIDSet(video_id)
        return
    
    mobj = re.search(r'''(.*?/st/flv/fileid/\d{8})(\d{2})(.*)''', url)
    if mobj is not None:
        url_prefix = mobj.group(1)
        file_order = mobj.group(2)
        url_suffix = mobj.group(3)
        for i in range(10):
            url = url_prefix+'%02d'+url_suffix
            url = url%(i)
            print url
            content = getContent(url, None, proxy)
            if content:
                part_save_path = save_path+'_%02d.flv'
                part_save_path = part_save_path%(i)
                f = open(part_save_path, "wb")
                f.write(content)
                f.close()
                print " File  Saved:[" + part_save_path + "]"
                log(" URL  Downloaded:[" + url + "]")
            else:
                break
        
        addToDownloadedVideoIDSet(video_id)
        #mergeFlv(save_path, i)
        

def mergeFlv(save_path, count):
    Merge_CMD = 'D:\\Program\\tools\\FLVMerge.exe'
    DEL_CMD = 'del '
    for i in range(count):
        part_save_path = save_path+'_%02d.flv'
        part_save_path = part_save_path%(i)
        Merge_CMD += ' "'+part_save_path+'"'
        DEL_CMD += ' "'+part_save_path+'"'
        
    #Merge_CMD += ' "'+save_path+'"'
    
    print Merge_CMD
    print DEL_CMD
        
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
    global proxy, host, get_flvurl_service_url
    
    #url=http%3A%2F%2Fv.youku.com%2Fv_show%2Fid_XNTgzNTkyMTY%3D.html&wantdown=haha&Submit=%E6%98%BE%E7%A4%BA%E4%B8%8B%E8%BD%BD%E5%9C%B0%E5%9D%80
    data = {'url': url,'wantdown': 'haha' ,'submit': '显示下载地址', }
    video_webpage = getContent(get_flvurl_service_url, data, proxy)

    video_real_url = ''
    video_title = ''
    mobj = re.search(r"""(?ms)target='_blank'>(.*?)</a></h3><br />.*?<p><a href='(.*?)'""", video_webpage)
    if mobj is not None:
        video_title = mobj.group(1).decode('utf-8').strip()
        #video_title = mobj.group(1).strip()
        video_real_url = mobj.group(2)
    
    return video_real_url, video_title

def downloadVideo(url):
    global proxy, work_path

    if hasBeenDownloadedBeforeByVideoPageURL(url):
        print "  Video:[" + url+ "] has been downloaded before, pass.\n"
        log("  Video:[" + url+ "] has been downloaded before, pass.\n")
        return
    
    video_real_url, video_title = getVideoInfo(url)
    saveFile(work_path+'\\videos', video_title, video_real_url, url);

def downloadAllVideos(url):
    global proxy, host, thread_count
    print url
    htmlcontent = getContent(url, None, proxy)
    
    pool = ThreadPool(thread_count)

    video_url_set = set()
    matched_groups = re.findall('''<a href="(http\://v\.youku\.com/v_show/id_.*?=\.html)"''', htmlcontent)
    for matched in matched_groups:
        #print matched.strip()
        video_url = matched.strip()
        video_url_set.add(video_url)

    for video_url in video_url_set:
        print video_url
        log(video_url)
        pool.queueTask(downloadVideo, (video_url))

    pool.joinAll()
    
def downloadAllPagesVideos(url):
    global proxy, host, thread_count
    print url
    content = getContent(url, None, proxy)
    
    all_page_content = ''
    matched_groups = re.findall('''<a href="(.*?)" title='第\d+页' charset=".*?">\d+</a>''', content)
    for matched in matched_groups:
        page_url = 'http://so.youku.com'+matched.strip()
        all_page_content += getContent(page_url, None, proxy)
    
    
    pool = ThreadPool(thread_count)

    video_url_set = set()
    matched_groups = re.findall('''<a href="(http\://v\.youku\.com/v_show/id_.*?=\.html)"''', all_page_content)
    for matched in matched_groups:
        #print matched.strip()
        video_url = matched.strip()
        video_url_set.add(video_url)

    for video_url in video_url_set:
        print video_url
        log(video_url)
        pool.queueTask(downloadVideo, (video_url))

    pool.joinAll()
#--------------------------------------------------------------------------------------
if __name__ == '__main__':
    clearLog()
    
    '''
    video_url = 'http://v.youku.com/v_show/id_XNTgzNTkyMTY=.html'
    video_url = 'http://v.youku.com/v_show/id_XNDczODA3NTI=.html'
    print getVideoInfo(video_url)
    downloadVideo(video_url)
    '''
    
    search_video_url = 'http://so.youku.com/search_video/q_%s/orderby_2'
    search_words = ['坚定信心促发展', '中国财经报道', '台湾万象', '防务新观察', '今日观察', '新闻30分', '晚间新闻']
    for word in search_words:
        downloadAllVideos(search_video_url%(urllib.quote_plus(word)))
    
    
    #search_video_url = 'http://so.youku.com/search_video/q_%s/orderby_3'
    #downloadAllPagesVideos(search_video_url%(urllib.quote_plus('哆啦a梦')))
    
    #convert_flv.convertFlv2Mp4underDir(work_path+'\\videos')
    
