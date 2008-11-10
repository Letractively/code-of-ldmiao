#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import urllib
import urllib2
import os
import sys
import random
import time
import socket


##############################################################################################################################################################################################

def converFromGB2312ToUTF8(onestr):
    newstr = onestr
    try:
        newstr = unicode(newstr, 'cp936', 'ignore')
    except:
        pass
    return newstr.encode('utf-8', 'ignore')


def getGB2312UnicodeString(onestr):
    newstr = onestr
    try:
        newstr = unicode(newstr, 'cp936', 'ignore')
    except:
        pass
    return newstr.encode('cp936', 'ignore')

def getBoardUpdateTime(board_id):
    update_date = open("update.conf").read()
    if not update_date or update_date == "":
        return None
    return time.localtime(float(update_date))
    
def updateBoardUpdateTime(board_id, pub_date):
    update_date = open("update.conf").read()
    
    if not update_date or update_date == "" or (update_date and float(update_date)<pub_date):
        f = open("update.conf", "w")
        f.write(str(pub_date))
        f.close()
##############################################################################################################################################################################################



#get the HTML Source from url through proxies
def getContent(url, proxies = None):
    if url.endswith(".jpg"):
        if proxies==None:
            print "  Download -->"+url
        else:
            print "  Download -->"+url+" through " + proxies['http']
    content = ""
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
            print "  Download "+url+" failed, " + str(test_time) + " times left~~~~"
            if test_time==1:
                proxies = None
            time.sleep(1)
    #print "  OK!"
    return content

def existFile(filename):
    if os.path.exists(filename):
        return True
    else:
        return False
##############################################################################################################################################################################################

def cleanArcicleContent(content):
    newcontent = content
    newcontent = newcontent.replace("\\n", "\n")
    newcontent = newcontent.replace("\\'", "'")
    newcontent = newcontent.replace("\\\"", "\"")
    newcontent = newcontent.replace("\\\\", "\\")
    newcontent = newcontent.replace("\\/", "/")
    newcontent = re.sub("\\\\r\[\\d*?(;\\d*?)*?[a-zA-Z]", "", newcontent)
    return newcontent

def getCleanText(content):
    
    #remove signature
    match_obj = re.compile("""^--\\n.*^[^\\n]*?\\[FROM\\:\\s*?\\d*?\\.\\d*?\\.\\d*?\\..*?\\]""", re.MULTILINE | re.DOTALL)
    if match_obj:
        content = match_obj.sub("", content)

    #remove the title
    match_obj = re.compile("""^发信人.*?^发信站.*?站内\\n""", re.MULTILINE | re.DOTALL)
    if match_obj:
        content = match_obj.sub("", content)
        
    
    #remove the reference article
    match_obj = re.compile("""^(【 在.*? 的大作中提到.*?】\\n((\\:.*?\n)|(\\n))*)|^(\\:.*?\\n)""", re.MULTILINE | re.DOTALL)
    if match_obj:
        content = match_obj.sub("", content)

    #remove the reference board
    match_obj = re.compile("""^【 以下文字转载自.*? 讨论区 】\\n""", re.MULTILINE | re.DOTALL)
    if match_obj:
        content = match_obj.sub("", content)
        
    #remove blank line
    match_obj = re.compile("""^\\n""", re.MULTILINE | re.DOTALL)
    if match_obj:
        content = match_obj.sub("", content)
       
    return content

def getArticleMetadata(html):
    match_obj = re.search("prints\('.*?发信站.*?\((\w\w\w)\s*?(\w\w\w)\s*?(\d*?)\s*?(\d*?\:\d*?\:\d*?)\s*?(\d*?)\)", html)
    if match_obj:
        match_groups = match_obj.groups()
        week, month, day, hms, year = match_groups
        pub_time = time.strptime(month+" "+day+" "+hms+" "+year, "%b %d %H:%M:%S %Y")
    else:
        pub_time = None

    from_ip = ""
    user_nick_name = ""


    match_objs = re.findall("\[FROM\: (\d*?\.\d*?\.\d*?\..*?)\]", html)
    if match_objs:
        from_ip = match_objs[len(match_objs)-1]

    match_obj = re.search("prints\('发信人.*?\((.*?)\)", html)
    if match_obj:
        user_nick_name = match_obj.group(1)

    match_obj = re.search("prints\('(.*?)'\);((o\.h\(0\);o\.t\(\);)|(attach\('))", html)
    content = match_obj.group(1)
    content = cleanArcicleContent(content)
    
    signature = ""
    match_obj = re.search("""^--\\n(.*?)^[^\\n]*?\\[FROM\\:\\s*?\\d*?\\.\\d*?\\.\\d*?\\..*?\\]""", content, re.MULTILINE | re.DOTALL)
    if match_obj:
        signature = match_obj.group(1)
    #print signature
    
    content_text = getCleanText(content)
    
    return pub_time, from_ip, user_nick_name, signature, content, content_text

def getAttachments(html):
    matched_objs = re.findall("""attach\('(.*?)', \d+, (\d+)\);""", html)
    #attachments = list()
    #for matched_obj in reversed(matched_objs):
        #print matched_obj
        #attach_name, attach_id = matched_obj
        #attachments.append((attach_name, attach_id))
        #url = "http://att.newsmth.net/att.php?p."874"."921153"."2554".jpg"
    return reversed(matched_objs)

def downloadArticle(board_id, article_id, article_type, thread_id, user_name, system_id, title, word_count, unknown_num1, unknown_num2, lastUpateTime, proxy=None):
    if article_type.find("d")!=-1 and lastUpateTime!=None:
        return None
    #print article_type, article_type.strip().find("@")
    if article_type.strip().find("@") == -1:
        return None
    
    url = "http://www.newsmth.net/bbscon.php?bid="+board_id+"&id="+article_id
    print "-", url
    html = getContent(url, proxy)
    
    match_obj = re.search("conWriter\(\d*?, (.*?), (\d*?), (\d*?), (\d*?), (\d*?),", html)
    if match_obj:
        match_groups = match_obj.groups()
        board_name, board_id, article_id, thread_id, reply_id = match_groups
        pub_time, from_ip, user_nick_name, signature, content, content_text = getArticleMetadata(html)
        attachments = getAttachments(html)

        if( lastUpateTime==None or pub_time==None or time.mktime(pub_time) > time.mktime(lastUpateTime) ):
            if attachments:
                #print url
                #print pub_time, time.mktime(pub_time)
                updateBoardUpdateTime(board_id, time.mktime(pub_time))
                
                downloadAttachments(board_id, article_id, attachments, user_name, proxy);
            
        else:
            return False
    return None

def downloadAttachments(board_id, article_id, attachments, user_name, proxy=None):
    for (attach_name, attach_id) in attachments:
        
        img_path_name = "images/www.newsmth.net/"+user_name+"_"+attach_name
        
        if existFile(img_path_name):
            print "  Image "+img_path_name+" exists, pass..."
        else:
            url = "http://att.newsmth.net/att.php?p."+board_id+"."+article_id+"."+attach_id+".jpg"
            content = getContent(url, proxy)
            print "  Save image to "+img_path_name
            f = open(img_path_name,"wb")
            f.write(content)
            f.close()
        
##############################################################################################################################################################################################

def downloadBoard(url, proxy=None):
    html = getContent(url, proxy)
    match_obj = re.search("docWriter\('(.*?)',(\d*?),\d*?,\d*?,\d*?,(\d*)", html);
    board_name = match_obj.group(1)
    board_id = match_obj.group(2)
    page_num = int(match_obj.group(3))

    lastUpateTime =  getBoardUpdateTime(board_id)
    print lastUpateTime
    
    idx = 0

    while page_num>0:
        url = "http://www.newsmth.net/bbsdoc.php?board="+board_name+"&page="+str(page_num)
        html = getContent(url, proxy)
        matched_objs = re.findall("""c\.o\((\d*?),(\d*?),'(.*?)','(.*?)\s*?',(\d*?),'(.*?)',(\d*?),(\d*?),(\d*?)\);""", html)

        for matched_obj in reversed(matched_objs):
            article_id, thread_id, user_name, article_type, system_id, title, word_count, unknown_num1, unknown_num2 = matched_obj

            downloaded = downloadArticle(board_id, article_id, article_type, thread_id, user_name, system_id, title, word_count, unknown_num1, unknown_num2, lastUpateTime, proxy)
            if downloaded==False:
                return
            elif downloaded==True:
                idx+=1
            elif downloaded==None:
                pass

        page_num = page_num - 1

##############################################################################################################################################################################################

if __name__=="__main__":
    #url = "http://www.newsmth.net/bbsdoc.php?board=NEU"
    #url = "http://www.newsmth.net/bbsdoc.php?board=NewExpress"
    #downloadBoard("http://www.newsmth.net/bbsdoc.php?board=NewExpress")
    #downloadBoard("http://www.newsmth.net/bbsdoc.php?board=Love")
    #downloadBoard("http://www.newsmth.net/bbsdoc.php?board=FamilyLife")
    #downloadBoard("http://www.newsmth.net/bbsdoc.php?board=Joke")
    #downloadBoard("http://www.newsmth.net/bbsdoc.php?board=WorkLife")
    #downloadBoard("http://www.newsmth.net/bbsdoc.php?board=RealEstate")
    #downloadBoard("http://www.newsmth.net/bbsdoc.php?board=CompMarket")
    #downloadBoard("http://www.newsmth.net/bbsdoc.php?board=Age")
    #downloadBoard("http://www.newsmth.net/bbsdoc.php?board=Mobile")
    #downloadBoard("http://www.newsmth.net/bbsdoc.php?board=MyWallet")
    
    proxy = {"http" : "http://beiwebcache2.core.hp.com:8088"}
    print socket.gethostname()
    if socket.gethostbyname(socket.gethostname()).startswith('192.168.'):
	proxy = None
    
	
    downloadBoard("http://www.newsmth.net/bbsdoc.php?board=MyPhoto", proxy)
    #if raw_input("Press any key to exit..."):
    #    pass
