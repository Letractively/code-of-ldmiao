#!/usr/bin/python
# -*- coding: utf-8 -*-

# http://www.moko.cc

import re
import urllib
import urllib2
import os
import sys
import random
import time
import md5  
import socket

import codecs

##############################################################################################################################################################################################

#timeout in seconds
timeout = 5 
socket.setdefaulttimeout(timeout)


proxyhost = "web-proxy.xxx.com"
proxyport = "8088"


proxies = {'http': 'http://'+proxyhost+':'+proxyport}
proxies = None

##############################################################################################################################################################################################

def converFromGB2312ToUTF8(onestr):
    newstr = onestr
    try:
        newstr = unicode(newstr, 'cp936', 'ignore')
    except:
        pass
    return newstr.encode('utf-8', 'ignore')

def htmlToText(html):
    html = html.replace("&nbsp;", " ")

    html = html.replace("&amp;", "&")

    html = html.replace("&quot;", "\"")
    html = html.replace("&#8220;", "\"")
    html = html.replace("&#8221;", "\"")
    
    html = html.replace("&apos;", "'")
    html = html.replace("&#039;", "'")
    html = html.replace("&#8217;", "'")

    html = html.replace("&#8230;", "...")
    
    html = html.replace("&lt;", "<")
    html = html.replace("&gt;", ">")
    
    return html

##############################################################################################################################################################################################

#Format String in sql
def fs(onestr):
    global db
    return db.escape_string(converFromGB2312ToUTF8(onestr))
    
    
def compute_md5(src):
    m = md5.new()
    m.update(src)   
    md5_value = m.hexdigest()
    return md5_value
    

##############################################################################################################################################################################################

def getContentLength(url):
    if url:
        print url
        match_obj = re.match("http://(.*?)(/.*)", url)
        host = match_obj.group(1)
        file = match_obj.group(2)
        #print host, file
        if host!=None and file!=None:
            test_time = 3
            #success = False
            #while(success == False):
            while(test_time>0):
                try:
                    conn = None
                    if proxies:
                        conn = httplib.HTTPConnection(proxyhost, proxyport)
                        conn.request("HEAD", url)
                    else:
                        conn = httplib.HTTPConnection(host)
                        conn.request("HEAD", file)
                    
                    response = conn.getresponse()
                    size = response.getheader('Content-length')
                    return int(size)
                except:
                    #success = False
                    test_time = test_time-1
                    print "Get ContentLength from:<"+url+"> failed, " + str(test_time) + " times left~~~~"

    return 0

#get the HTML Source from url through proxies
def getContent_nouse(url, data=None, proxies=None):
    time.sleep(random.randrange(2,5,1))

    '''change space char into %20'''
    url = url.replace(" ", "%20")

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
#        except urllib2.HTTPError, e:
#            print 'The server couldn\'t fulfill the request.'
#            print 'Error code: ', e.code
#            content = None
#            break
        #except urllib2.URLError, e:
        #    print 'We failed to reach a server.'
        #    print 'Reason: ', e.reason
        #    content = None
        #    break
        except:
            content = None
            #success = False
            test_time = test_time-1
            print "Get:["+url+"] failed, " + str(test_time) + " times left~"
            time.sleep(random.randrange(60,120,1))
        
    return content


def getContent(url):
    '''change space char into %20'''
    url = url.replace(" ", "%20")
    content = None
    test_time = 3
    #success = False
    #while(success == False):
    while(test_time > 0):
        try:
            filehandle = urllib.urlopen(url, proxies=proxies)
            content = filehandle.read()
            #success = True
            test_time = 0
        except:
            content = None
            #success = False
            test_time = test_time - 1
            print "Download failed, " + str(test_time) + " times left~~~~"
            time.sleep(random.randint(90, 120))
            
    return content

def getDirName(url):
    dirname = url[(url.rfind('/')+1):(len(url))]
    dirname = getChineseFromURL(dirname)
    if dirname == None:
        dirname = "images"
    return dirname

def existFile(filename):
    if os.path.exists(filename):
        return True
    else:
        return False

def log(str):
    if str:
        str = str.strip()
        if str!='':
            f = codecs.open("/home/ldmiao/data/pictures/moko_data/download_images_log.log", "a", "utf-8")
            f.write(str+u'\n')
            f.close()

def log_girl(str):
    if str:
        str = str.strip()
        if str!='':
            f = codecs.open("/home/ldmiao/data/pictures/moko_data/download_girls_log.log", "a", "utf-8")
            f.write(str+u'\n')
            f.close()
            
def saveImage(dirname, img_url, girl_id, img_name=None):
    print "download image:" + img_url
    
    if not existFile(dirname):
        try:
            print "Create dir: "+dirname
            os.mkdir(dirname)
        except:
            dirname = "images"
            if not existFile(dirname):
                print "Create dir: "+dirname
                os.mkdir(dirname)

    #content = getContent(img_url)
    #if content is None:
    #    return None
    
    if img_name is None:
        #image_md5 = compute_md5(content) 
        image_md5 = compute_md5(img_url)
        img_path_name = dirname + "/" + image_md5 + ".jpg"
    else:
        img_path_name = dirname + "/" + img_name
        image_md5 = img_name
    
    if existFile(img_path_name):
        print "\033[31m File " + img_path_name + " already exists, pass~~ \033[0m"
        return None
    
    content = getContent(img_url)
    if content is None:
        return None
    
    try:
        f = open(img_path_name, "wb")
        f.write(content)
        f.close()
        print "\033[33m Image " + img_path_name + " SAVE! \033[0m" 
        log(girl_id+'/'+image_md5+','+img_url)
    except:
        print "Error occured, pass~"
        return None
        
    return image_md5



# #############################################################################################################################################################################################

def downloadPicsInAlbum(dir, album_url, girl_id):  
    base_url = "http://www.moko.cc"
    html = getContent(album_url)
    #print html[:100]

    matched_objs = re.findall('''<div class="info r">\s*<h6 .*?>(.*?)</h6>\s*<p class="[^"]+">(\s+<img class="bg r".*? />)?\s+(.*?)</p>.*?<img class="borderOn" src="([^"]*?)"''', html, re.DOTALL)
    if matched_objs == None or len(matched_objs) == 0:
        print "\n \033[31m Can not extract the meta data from " + album_url + "\033[0m \n"
        return 0
    
    matched_obj = matched_objs[0]
    album_datetime, nouse, album_title, cover_source = matched_obj
    album_title = album_title.strip()
    
    cover_file_name = os.path.basename(cover_source)
    
    album_log_file = open('%s/%s.log'%(dir, cover_file_name), 'w')
    album_log_file.write('title:%s\n'%(album_title))
    album_log_file.write('date:%s\n'%(album_datetime))
    
    if cover_source.find('http://')==-1:
        cover_source = base_url + cover_source
    cover_md5 = saveImage(dir, cover_source, girl_id, cover_file_name)
    album_log_file.write('cover:%s\n'%(cover_source))
    print album_datetime, album_title, cover_source, cover_md5
        
        
    down_pic_count = 0
    
    pattern_1_OK = 0
    pattern_2_OK = 0
    pattern_3_OK = 0
    
    matched_objs = re.findall("""<div class="pic dashedOn">\s*<a href="([^"]*?)" """, html,  re.DOTALL)  
    if matched_objs == None or len(matched_objs) == 0:
        print "\n \033[31m Can not use pattern #1 to extract the pics from " + album_url + "\033[0m \n"
        pattern_1_OK = 0
    else:
        pattern_1_OK = 1

        for matched_obj in matched_objs:
            img_url = matched_obj
            if img_url.find('http://')==-1:
                img_url = base_url + img_url
            md5 = saveImage(dir, img_url, girl_id, os.path.basename(img_url))
            album_log_file.write('picture:%s\n'%(img_url))
            print img_url, md5, girl_id
            down_pic_count += 1

    if pattern_1_OK == 0:
        matched_objs = re.findall("""<img class="l" src="([^"]*?)" """, html, re.DOTALL)
        if matched_objs == None or len(matched_objs) == 0:
            print "\n \033[31m Can not use pattern #2 to extract the pics from " + album_url + "\033[0m \n"
            pattern_2_OK = 0
        else:
            pattern_2_OK = 1
    
            for matched_obj in matched_objs:
                img_url = matched_obj
                img_url = img_url.replace("/thumb/", "/src/", 1)
                if img_url.find('http://')==-1:
                    img_url = base_url + img_url
                md5 = saveImage(dir, img_url, girl_id, os.path.basename(img_url))
                album_log_file.write('picture:%s\n'%(img_url))
                print img_url, md5, girl_id
                down_pic_count += 1

    if pattern_2_OK == 0:
        matched_objs = re.findall("""<img src="([^"]*?)" title="[^"]*?" alt="[^"]*?" />""", html, re.DOTALL)
        if matched_objs == None or len(matched_objs) == 0:
            print "\n \033[31m Can not use pattern #3 to extract the pics from " + album_url + "\033[0m \n"
            pattern_3_OK = 0
        else:
            pattern_3_OK = 1
    
            for matched_obj in matched_objs:
                img_url = matched_obj
                #img_url = img_url.replace("thumb", "src", 1)
                if img_url.find('http://')==-1:
                    img_url = base_url + img_url
                md5 = saveImage(dir, img_url, girl_id, os.path.basename(img_url))
                album_log_file.write('picture:%s\n'%(img_url))
                print img_url, md5, girl_id
                down_pic_count += 1
    
    album_log_file.close()
    
    return down_pic_count
    

def downloadAlbumInGirlPage(dir, girl_id, girl_name):
    base_url = "http://www.moko.cc"
    girl_homepage = "http://www.moko.cc/" + girl_id
    girl_indexpost = "http://www.moko.cc/post/" + girl_id + "/indexpost.html" #http://www.moko.cc/post/zhangyinghan/indexpost.html
    #girl_icon = "http://www.moko.cc/images/index_user/" + girl_id + ".jpg"  #http://www.moko.cc/images/index_user/huangfei.jpg
    
    
    if not existFile(dir):
        try:
            print "Create dir: "+dir
            os.makedirs(dir)
        except:
            pass
    
    # ####################################################################################################
    girl_icon = None
    html = getContent(girl_homepage)
    matched_objs = re.findall("""<img id="idPicture" class="userIcon borderOn" src="([^"]+)" />""", html, re.DOTALL)
    if matched_objs is not None and len(matched_objs) > 0:
        girl_icon = matched_objs[0]
    
    
    girl_log_file = open('%s/girl.log'%(dir), 'w')
    girl_log_file.write('id:%s\n'%(girl_id))
    girl_log_file.write('name:%s\n'%(girl_name.strip()))
    if girl_icon is not None:
        girl_log_file.write('head:%s\n'%(girl_icon))
    girl_log_file.close()
    
    if girl_icon is not None:
        icon_md5 = saveImage(dir, girl_icon, girl_id, 'head.jpg')
    
    
    # ####################################################################################################
    
    html = getContent(girl_indexpost)
    #extract_start = html.index("div class=\"show l")
    #extract_start = 7000
    #print html[extract_start:extract_start + 500]
    
    page_count = 1
    
    matched_objs = re.findall("""<a href="(/post/[^/^"]+/indexpage/(\d+)\.html)" class="l" onfocus="[^"]*?">\d+</a>""", html, re.DOTALL)
    if matched_objs is not None and len(matched_objs) > 0:
        for matched_obj in reversed(matched_objs):
            page_url, page_num = matched_obj
            page_num = int(page_num)
            if page_num>page_count:
                page_count = page_num
        
        print "Extract page count:%d from %s"%(page_count, girl_indexpost)
        
    if page_count>1:
        for page_num in range(2, page_count+1):
            html += getContent('%s/post/%s/indexpage/%d.html'%(base_url, girl_id, page_num))
        

    #matched_objs = re.findall("""<div class="show l".*?<a class="coverBg.*?href="([^"]*?)">.*?<img class="borderOn" src="([^"]*?)" """, html, re.DOTALL)
    matched_objs = re.findall("""href=['"]/post/([\d/]+)\.html['"]>""", html, re.DOTALL)
    if matched_objs == None or len(matched_objs) == 0:
        print "Can not use pattern 1 to extract the album list from " + girl_indexpost
    
    downloaded_url_set = set()
    
    album_count = 0
    pic_count = 0
    for matched_obj in reversed(matched_objs):
        album_url = matched_obj
        print "##################################################"
        album_url = base_url + "/post/" + album_url + ".html"
        if album_url in downloaded_url_set:
            continue
        else:
            downloaded_url_set.add(album_url)

        album_count += 1
        print album_count, album_url
        pic_count += downloadPicsInAlbum(dir, album_url, girl_id)

    print "Download " + str(album_count) + " albums of " + girl_id + " @ " + girl_indexpost
    print "Download " + str(pic_count) + " pics of " + girl_id + " @ " + girl_indexpost
    return pic_count
    
    
def downloadAllGirls(dir, index_pages):
    girl_count = 0
    pic_count = 0
    
    girl_id_sets = set()
    girl_id_sets.add('tongjia')
    girl_id_sets.add('corallin33')
    for index_page in index_pages:
        #index_page = "http://www.moko.cc/logout_girlvote/index.html"
        #index_page = "http://www.moko.cc/hotvisit.html"
        #index_page = "http://www.moko.cc/MOKO_POST_ORDER_MOKO/1/postList.html"
        html = getContent(index_page)
    
        isPatternMatched = 1
    
        matched_objs = re.findall("""<div class="l">.*?<a class="imgBorder" href='(.*?)' .*?<img src="[^"]*?".*?<a class="mainWhite font12".*?>(.*?)</a>""", html, re.DOTALL)
        if matched_objs == None or len(matched_objs) == 0:
            print "Can not extract girls from " + index_page + " with pattern 1"
            isPatternMatched = 0
    
        if isPatternMatched == 0:
            matched_objs = re.findall("""<a class="mainWhite" href="([^"]*?)" target="_blank" title="(.*?)">""", html)
            if matched_objs == None or len(matched_objs) == 0:
                print "Can not extract girls from " + index_page + " with pattern 2"
            
        if isPatternMatched == 0:
            matched_objs = re.findall("""<a class="mainWhite" href="([^"]*?)" target="_blank">(.*?)</a>""", html)
            if matched_objs == None or len(matched_objs) == 0:
                print "Can not extract girls from " + index_page + " with pattern 3"
                #return 0
        if matched_objs is None or len(matched_objs)==0:
            continue
        for matched_obj in matched_objs:
            girl_homepage, girl_name = matched_obj
            print girl_name
            girl_id = girl_homepage[girl_homepage.find('/')+1:girl_homepage.rfind('/')]
            
            if girl_id.find('/')==-1:
                girl_id_sets.add((girl_id, girl_name))
    

    base_url = "http://www.moko.cc"
    start_girl_id = "zhangyinghan"
    is_get_start_id = 0

    for girl_id, girl_name in girl_id_sets:
        new_dir = dir +  "/" + girl_id
        
        log_girl(girl_id)

        girl_homepage = base_url + '/'+ girl_id + "/"
        print girl_count, girl_homepage, girl_id
        girl_count += 1
        
        try_times = 3
        down_pic_count = 0
        while (down_pic_count == 0 and try_times > 0):
            down_pic_count = downloadAlbumInGirlPage(new_dir, girl_id, girl_name)
            try_times -= 1
        
        pic_count += down_pic_count
        #time.sleep(3) 

    print "Total downloaded girls: " + str(girl_count)
    print "Total downloaded pics: " + str(pic_count)

##############################################################################################################################################################################################


if __name__ == "__main__":
    dir = "data"
    index_pages = ["http://www.moko.cc/logout_girlvote/index.html", "http://www.moko.cc/hotvisit.html"]
    for i in range(1, 9):
        index_page = "http://www.moko.cc/MOKO_POST_ORDER_MOKO/"+str(i)+"/postList.html"
        index_pages.append(index_page)
    for i in range(1, 30):
        index_page = "http://www.moko.cc/MOKO_POST_ORDER_VIEWCOUNT/"+str(i)+"/postList.html"
        index_pages.append(index_page)
    downloadAllGirls(dir, index_pages)
    
    
    
