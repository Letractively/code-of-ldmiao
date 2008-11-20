#!/usr/bin/env python
#coding=utf-8
"""
LrcRetriever.py
从baidu上获取LRC格式歌词的测试脚本
原理是在www.baidu.com搜索"歌名 filetype:lrc"，在搜索结果中查看第一个搜索结果的百度快照，就是LRC歌词了。
实验表明，如果搜索结果的第一条不是LRC歌词，那其它的搜索结果就不是想要的，这时放弃比较好。

v1.0
Created by RunningOn
RunningOn@gmail.com
Nov 17, 2008
"""

import urllib, urllib2, sys

def get_lyric(song_name, output_file_name = ''):
    """
    下载歌词并返回。如果指定了文件名，则同时保存到文件
    song_name: 歌曲的名字，搜索用的关键词。是一个utf-8的字符串
    output_file_name: 保存的文件名。如果为空则不保存。
    返回LRC格式的歌词，注意是普通str不是unicode，行与行之间用\r分开
    如果没有找到歌词，返回空串
    """
    lyric = ''
    try:
        query=urllib.urlencode({'wd':song_name.encode('gb18030')})   #把歌名转化为URL中可以使用的格式
        URL = 'http://www.baidu.com/s?%s+filetype%%3Alrc&cl=3' % (query)
        webfd = urllib2.urlopen(URL)
        lyricpage = webfd.read()    #获取网页内容
        webfd.close()
        #网页中"http://cache.baidu.com/c?m=....&user=baidu"就是百度快照地址了，取第一个就可以了
        index1 = lyricpage.find('<a href="http://cache.baidu.com')
        index2 = lyricpage.find('user=baidu')
        if index1 == -1 or index2 == -1:    #没有找到，返回空串
            return ''
        if lyricpage[index1-12:index1] != 'LRC/Lyric - ':   #第一个链接不是LRC文件，放弃。
            return ''
        url = lyricpage[index1+9: index2+10]#记下第一个百度快照的链接
        webfd = urllib2.urlopen(url)        #打开百度快照
        lyricpage = webfd.read()
        webfd.close()
        index1 = lyricpage.find('<body>')   #<body>和</body>之间的就是歌词了。
        index2 = lyricpage.rfind('</body>')
        raw_lyric = lyricpage[index1+6:index2+7]          #获得原始歌词，还要加工一下
        raw_lyric = raw_lyric.replace('<BR>', '\n')     #把HTML中的<BR>换为换行符
        #删去歌词中所有的<...> HTML代码
        bracket_left = []
        bracket_right = [-1]
        location = 0
        while True:     #找到所有的 <
            location = raw_lyric.find('<', location+1)
            if location == -1:
                break
            bracket_left.append(location)
        location = 0
        while location != -1:   #找到所有的 >
            location = raw_lyric.find('>', location+1)
            bracket_right.append(location)
        num = len(bracket_left)
        #下面一行是把所有的<...>之外的字符串连接起来，稍有点难懂，但比较pythonic
        #这样的拼接字符串的方法是比较快的，详细的比较我参考的是这篇文章：http://www.skymind.com/~ocrow/python_string/
        lyric = ''.join(raw_lyric[bracket_right[i]+1:bracket_left[i]] for i in xrange(num))
        if output_file_name != '':  #把歌词保存到文件
            fd = open(output_file_name, 'w')
            fd.write(lyric)
            fd.close()
        return lyric
    except Exception, msg:
        sys.stderr.write('Error when retrieving the lyric: %s\n' % msg)
        return ''

if __name__ == '__main__':
    #Example:
    lyric = get_lyric(u'圣诞结', u'圣诞结.lrc')
    if lyric == '':
        print 'No lyrics found'
    else:
        print lyric #如果是在Linux下，utf-8的locale，请print lyric.decode('gb18030')，不然是乱码
