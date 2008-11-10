#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import urllib
import urllib2
import os
import sys
import random
import time

import MySQLdb
import codecs

import md5

##############################################################################################################################################################################################

def converFromGB2312ToUTF8(onestr):
    newstr = onestr
    try:
        newstr = unicode(newstr, 'cp936', 'ignore')
    except:
        pass
    return newstr.encode('utf-8', 'ignore')

##############################################################################################################################################################################################
db = None

def getDB():
    global db
    if db is None:
        db=MySQLdb.connect(host="hplcws1.hpl.hp.com",port=3306,user="smth",passwd="smth",db="smth",charset="utf8")
    return db

def closeDB():
    global db
    if(db):
        db.close()

#Format String in sql
def fs(onestr):
    global db
    return db.escape_string(converFromGB2312ToUTF8(onestr))

def saveToDB(board_id, article_id, thread_id, reply_id, user_name, user_nick_name, system_id, url, title, content, pub_time, from_ip, word_count, unknown_num1, unknown_num2, html):
    db=getDB()
    c=db.cursor()

    pub_time_str = time.strftime("%Y-%m-%d %H:%M:%S", pub_time)

    article_md5 = user_name+"_"+article_id+"_"+pub_time_str
    #article_md5 = md5.new(user_name+"_"+article_id+"_"+pub_time_str).digest()
    thread_md5 = ""
    reply_md5 = ""

    try:
        sql = "INSERT INTO `article` (`article_md5`, `thread_md5`, `reply_md5`, `article_id`, `board_id`, `thread_id`, `reply_id`, `system_id`, `user_name`, `user_nick_name`, `url`, `title`, `content`, `pub_time`, `from_ip`, `word_count`, `unknown_num1`, `unknown_num2`, `html`) values ('"+article_md5+"', '"+thread_md5+"', '"+reply_md5+"', "+article_id+", "+board_id+", "+thread_id+", "+reply_id+", "+system_id+", '"+user_name+"', '"+fs(user_nick_name)+"', '"+fs(url)+"', '"+fs(title)+"', '"+fs(content)+"', '"+pub_time_str+"', '"+from_ip+"', "+word_count+", "+unknown_num1+", "+unknown_num2+", '"+fs(html)+"')"
        #print sql
        c.execute(sql)
        db.commit()
        print article_md5 + " saved!"
        return True
    except:
        return False


def getBoardUpdateTime(board_id):
    db=getDB()
    c=db.cursor()
    sql = "SELECT `pub_time` FROM `article` WHERE `board_id`="+board_id+" ORDER BY `pub_time` desc LIMIT 1"
    print sql
    c.execute(sql)
    row = c.fetchone()
    if row:
        print row[0].strftime("%Y-%m-%d %H:%M:%S")
        return time.strptime(row[0].strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
    else:
        return None

def saveBoard(board_id, board_name):
    db=getDB()
    c=db.cursor()
    try:
        sql1 = "INSERT INTO `board` (`id`, `name`) values ("+board_id+", '"+board_name+"')"
        print sql1
        c.execute(sql1)
        db.commit()
    except:
        pass
    
    try:
        sql2 = "UPDATE `board` SET `last_update_time`=NOW() WHERE `id`="+board_id
        print sql2
        c.execute(sql2)
        db.commit()
    except:
        pass

def saveBoardUpdateNum(board_id, board_name, update_num):
    update_num_str = str(update_num)
    db=getDB()
    c=db.cursor()
    try:
        sql = "UPDATE `board` SET `update_num`="+update_num_str+" WHERE `id`="+board_id
        print sql
        c.execute(sql)
        db.commit()
    except:
        pass
    
    try:
        sql = "INSERT INTO `board_update_history` (`id`, `name`, `update_num`, `last_update_time`) VALUES ( "+board_id+", '"+board_name+"', "+update_num_str+", NOW() )"
        print sql
        c.execute(sql)
        db.commit()
    except:
        pass

def getAllBoards():
    db=getDB()
    c=db.cursor()
    sql = "SELECT `name` FROM `board`"
    print sql
    c.execute(sql)
    row = c.fetchone()
    boards = set()
    while row:
        boards.add(row[0])
        row = c.fetchone()

    return boards
    
    
##############################################################################################################################################################################################

proxy_set = None

def getProxies():
    
    print "Proxy List:"
    
    global proxy_set
    proxy_set = set()
    
    #proxy_set.add('http://web-proxy.hpl.hp.com:8088')
    #proxy_set.add('http://atlwebcache.core.hp.com:8080')
    proxy_set.add('http://beiwebcache2.core.hp.com:8080')
    proxy_set.add('http://beiwebcache1.core.hp.com:8080')
    #proxy_set.add('http://web-proxy.austin.hp.com:8080')
    
    #proxy_set.add('http://proxy.cce.cpqcorp.net:8080')
    #proxy_set.add('http://atlwebcache3.core.hp.com:8080')
    
    #proxy_set.add('http://web-proxy.austin.hp.com:8080')
    #proxy_set.add('http://web-proxy.austin.hp.com:8080')
    #proxy_set.add('http://web-proxy.austin.hp.com:8080')
    #proxy_set.add('http://web-proxy.austin.hp.com:8080')
    
    
    content = getContent('http://autocache.hp.com')
    f = open("autoproxy.txt", "w")
    f.write(content)
    f.close()
    matched_groups = re.findall('\WPROXY\s*?(.*?):(\d{1,})', content)
    for matched in matched_groups:
        print matched
        host = matched[0].strip()
        port = matched[1].strip()
        if host != 'localhost' and host != '131.168.229.119':
            #proxy_set.add("http://"+host+":"+port)
            print host+":"+port
            
def getOneProxy():
    global proxy_set
    if(proxy_set==None):
        getProxies()
    if(proxy_set==None or len(proxy_set)==0):
        return None
    randm_num = random.randint(0, len(proxy_set)-1)
    i=0
    for proxy in proxy_set:
        if i==randm_num:
            return {"http" : proxy}
        i = i+1
    #return {'http': 'http://beiwebcache1.core.hp.com:8080'}




##############################################################################################################################################################################################



#get the HTML Source from url through proxies
def getContent(url, proxies = None):
    if proxies==None:
        print "Download ---->"+url
    else:
        print "Download ---->"+url+" through " + proxies['http']
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
            print "Download "+url+" failed, " + str(test_time) + " times left~~~~"
            time.sleep(1)
    return content

##############################################################################################################################################################################################


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
    content = content.replace("\\n", "\n")

    return pub_time, from_ip, user_nick_name, content


def downloadArticle(board_id, article_id, article_type, thread_id, user_name, system_id, title, word_count, unknown_num1, unknown_num2, lastUpateTime):
    url = "http://www.newsmth.net/bbscon.php?bid="+board_id+"&id="+article_id
    print url
    html = getContent(url, getOneProxy())

    match_obj = re.search("conWriter\(\d*?, (.*?), (\d*?), (\d*?), (\d*?), (\d*?),", html)
    if match_obj:
        match_groups = match_obj.groups()
        board_name, board_id, article_id, thread_id, reply_id = match_groups
        pub_time, from_ip, user_nick_name, content = getArticleMetadata(html)

        #print board_name, board_id, article_id, thread_id, reply_id, time.strftime("%Y-%m-%d %H:%M:%S", pub_time), from_ip, user_name, user_nick_name, content

        if( lastUpateTime==None or pub_time==None or time.mktime(pub_time) > time.mktime(lastUpateTime) ):
            saved = saveToDB(board_id, article_id, thread_id, reply_id, user_name, user_nick_name, system_id, url, title, content, pub_time, from_ip, word_count, unknown_num1, unknown_num2, html)
            if saved:
                return True
            else:
                return None
        else:
            if article_type.find("d")!=-1:
                return None
            return False
    return None

##############################################################################################################################################################################################


def downloadBoard(url):
    html = getContent(url, getOneProxy())
    match_obj = re.search("docWriter\('(.*?)',(\d*?),\d*?,\d*?,\d*?,(\d*)", html);
    board_name = match_obj.group(1)
    board_id = match_obj.group(2)
    page_num = int(match_obj.group(3))
    
    saveBoard(board_id, board_name)

    lastUpateTime =  getBoardUpdateTime(board_id)

    idx = 0

    while page_num>0:
        url = "http://www.newsmth.net/bbsdoc.php?board="+board_name+"&page="+str(page_num)
        html = getContent(url, getOneProxy())
        matched_objs = re.findall("""c\.o\((\d*?),(\d*?),'(.*?)','(.*?)\s*?',(\d*?),'(.*?)',(\d*?),(\d*?),(\d*?)\);""", html)

        for matched_obj in reversed(matched_objs):
            article_id, thread_id, user_name, article_type, system_id, title, word_count, unknown_num1, unknown_num2 = matched_obj
            #print idx, article_id, thread_id, user_name, system_id, title, word_count, unknown_num1, unknown_num2
            #if(article_type != "d"):
            downloaded = downloadArticle(board_id, article_id, article_type, thread_id, user_name, system_id, title, word_count, unknown_num1, unknown_num2, lastUpateTime)
            if downloaded==False:
                saveBoardUpdateNum(board_id, board_name, idx)
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
    #downloadBoard("http://www.newsmth.net/bbsdoc.php?board=ITExpress")
    #print getBoardUpdateTime("95")
    
    boards_set = getAllBoards()
    for board in boards_set:
        downloadBoard("http://www.newsmth.net/bbsdoc.php?board="+board)
