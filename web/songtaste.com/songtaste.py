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

#proxy = {'http': 'http://beiwebcache1.core.hp.com:8080'}
proxy = None
save_path = 'songs'

#get the HTML Source from url through proxies
def getContent(url, proxies = None):
    if proxies==None:
        print "  Get: "+url
    else:
        print "  Get: "+url+" through " + proxies['http']
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
            print "  Get: "+url+" failed, " + str(test_time) + " times left~~~~"
            time.sleep(10)
    return content

def getSong(song_id, order):
    global proxy
    global save_path
    
    url = 'http://songtaste.com/play.php?song_id='+song_id
    htmlcontent = getContent(url, proxy)
    match_obj = re.search('''WrtSongLine\("(\d+)", "(.*?)\s*", ".*?", "\d*", "\d*", "(.*?)"\);''', htmlcontent)
    
    if not match_obj:
        return
    
    song_id = match_obj.group(1).strip()
    song_name = match_obj.group(2).strip()
    song_url = match_obj.group(3).strip()
    #print " ", song_id, song_name, song_url
    
    try:
        saveSong(order, song_id, song_name, song_url, save_path)
    except:
        print traceback.format_exc()

def existFile(filename):
    if os.path.exists(filename):
        return True
    else:
        return False
        
def saveSong(order, song_id, song_name, song_url, save_path):
    global proxy
    order = int(order)
    file_name = song_name.replace('\\','')
    file_name = file_name.replace('/', '')
    file_name = file_name.replace(':', '-')
    file_name = file_name.replace('*', '-')
    file_name = file_name.replace('?', '-')
    file_name = file_name.replace('"', '-')
    file_name = file_name.replace('<', '-')
    file_name = file_name.replace('>', '-')
    file_name = file_name.replace('|', '-')
    song_save_path = save_path+'/'+"%03d"%order+'_'+song_id+'_'+file_name+song_url[song_url.rfind('.'):]
    if existFile(song_save_path):
        print "  Song:", song_save_path, "exists, pass\n"
        return
    
    print "  Download Song:", song_save_path
    content = getContent(song_url, proxy)
    if content:
        print "  Save song to " + song_save_path +"\n"
        f = open(song_save_path,"wb")
        f.write(content)
        f.close()
    
def getAllRecommendedSongs(url):
    global proxy
    htmlcontent = getContent(url, proxy)
    matched_groups = re.findall('''WL\("(\d+)", "(\d+)","(.*?)\s+",".*?"\);''', htmlcontent)
    for matched in matched_groups:
        print '-'*20 ,matched, '-'*20 
        order = matched[0].strip()
        song_id = matched[1].strip()
        song_name = matched[2].strip()
        getSong(song_id, order)
        
    
if __name__=="__main__":
    #url = 'http://songtaste.com/user/36692/allrec'
    #url = 'http://songtaste.com/user/36692/allrec/2'
    #url = 'http://songtaste.com/user/36692/allrec/3'
    url = 'http://songtaste.com/user/36692/allrec/4'
    getAllRecommendedSongs(url)
    
    
    
    