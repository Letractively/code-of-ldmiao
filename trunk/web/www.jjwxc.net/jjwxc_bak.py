#!/usr/bin/python
# -*- coding:  gb2312-*-
"""
__version__ = "$Revision: 0.01 $"
__date__ = "$Date: 2006-7-15 01:08:00 $"
"""

from PythonCard import dialog, model
import wx
import os, sys, time, re
from urllib import urlopen
from threading import Thread


chapterNotExistString="""作者可能删除了文件，或者暂时不对外开放.请按下一章继续阅读!"""


class JJWXCArticleSys(model.Background):
    
    def on_filechooser_mouseClick(self, event):
        result = dialog.directoryDialog(self, '选择小说下载后保存的目录', 'a')
        if result.accepted:
            self.components.savedir.text = result.path

    def on_okbutton_mouseClick(self, event):
        novelurls = self.components.novellinks.text
        if not novelurls:
            result = dialog.alertDialog(self, 'Novel link needed', 'ERROR')
            return
        savedir = self.components.savedir.text
        if not savedir or savedir =='':
            result = dialog.alertDialog(self, 'Save to dir needed', 'ERROR')
            return
        novelProcessThread = NovelProcess(self, novelurls, savedir)
        novelProcessThread.start()
        self.disableComponent()
        #novelProcessThread.join()

    def enableComponent(self):
        #enable the button
        self.components.okbutton.enabled = 1
        
    def disableComponent(self):
        #enable the button
        self.components.okbutton.enabled = 0
        
    def displayStatus(self, percent):
        self.components.processgauge.value = percent*100
        self.components.processpercent.text = str(int(percent*100))+'%'
        
    def addLog(self, logstr):
        self.components.log.appendText(logstr)

class NovelProcess(Thread):
    savedir = None
    novels = None
    chaplist = None
    jjwxcapp = None
    
    def __init__(self, jjwxcapp, novelurls, savedir):
        Thread.__init__(self)
        self.jjwxcapp = jjwxcapp
        self.savedir = savedir
        pattern = re.compile(r"""(http://www.jjwxc.net/onebook.php\?novelid=\d{1,})\s*(.*?)\n""", re.IGNORECASE| re.DOTALL)
        self.novels = pattern.findall(novelurls)
            

    def run(self):
        self.process()
    
    def getTotalChapterNum(self, url):
    	noveltitle = None
        self.jjwxcapp.addLog('[Novel index] ['+ time.strftime("%X") +'] ' + url +'\n')
        self.jjwxcapp.addLog('connect... ')
        text = None
        for i in range(1,11):
            text = self.getHtmlContent(url)
            if text:
                break
            else:
                self.jjwxcapp.addLog("reconnect "+str(i)+': ')
                self.waitawhile()

        if not text:
            self.jjwxcapp.enableComponent()
            return (0, None)
        else:
            pattern = re.compile(r"""<ul class="rightul">.*?<title>(.*?)</title></li>""", re.IGNORECASE| re.DOTALL)
            match_obj =  pattern.search(text)
            if match_obj:
                noveltitle = match_obj.group(1)
            else:
                self.jjwxcapp.enableComponent()
                print text
            
            pattern = re.compile(r"""<td>\s*?<a href=/onebook.php\?novelid=\d{1,}&chapterid=(\d{1,})>(.*?)</a>\s*?</td>\s*?<td>\s*?(.*?)\s*?</td>""", re.IGNORECASE| re.DOTALL)
            self.chaplist =  pattern.findall(text)
            if len(self.chaplist)>=1:
                return (int(self.chaplist[len(self.chaplist)-1][0]), noveltitle)
            else:
                return (0, noveltitle)

    def downloadNovel(self, novelurl, novelname):
        print '>>>>>>',novelname
        noveltitle = None
        chapnum, noveltitle = self.getTotalChapterNum(novelurl)
        print '>>>>>>',novelname, noveltitle
        if chapnum <=0:
            return
        if not novelname or novelname=='' or novelname==' ':
            if noveltitle:
                novelname = noveltitle
            else:
            	pattern = re.compile(r"""novelid=(\d{1,})""", re.IGNORECASE| re.DOTALL)
            	match_obj = pattern.search(novelurl)
            	novelid = match_obj.group(1)
                novelname = 'novel_' + novelid
        fd = open(self.savedir + '\\' + novelname + '.htm','w')
        fd.write('<head><title>' + noveltitle + '</title></head>\n')
        fd.write('<body bgcolor="#EEFAEE">');
        
        self.writeChapterMenu(fd, novelurl, noveltitle)

        downloadchapcount = 0;
        for chap in self.chaplist:
            i = int(chap[0])
            self.jjwxcapp.addLog('['+str(i)+'/'+str(chapnum)+'] ['+ time.strftime("%X") +'] ' + novelurl + '&chapterid=' + str(i) +'\n')
            self.jjwxcapp.addLog('connect... ')
            
            chapurl = novelurl + '&chapterid=' + str(i)
            
            #disable the componenets while downloading
            self.jjwxcapp.disableComponent()
            
            cleannoveltext = self.getRealContent(chapurl)
            #print cleannoveltext
            #self.jjwxcapp.addLog(self.chaplist[i-1][1]+'  '+self.chaplist[i-1][2]+'\n')
            fd.write('<a name="'+str(i)+'">\n')
            fd.write(cleannoveltext)
            fd.write('<div align="right"><a href="#menu">回目录</a></div>\n')
            fd.write('<hr>\n')
            fd.flush()
            if i < chapnum:
                self.waitawhile()
            downloadchapcount = downloadchapcount + 1
            self.jjwxcapp.displayStatus(i/float(chapnum))
        
        fd.write('</body>');
        fd.close()

        #for chap in self.chaplist:
        #    self.jjwxcapp.addLog(chap[0]+'\t'+chap[1]+'\t'+chap[2]+'\n')

        self.jjwxcapp.addLog('Novel download successful, total ' + str(chapnum) + ' chapters.'+'\n')
        #self.jjwxcapp.addLog('Save to dir: '+self.savedir+'\n')
        self.jjwxcapp.enableComponent()     
        
    def process(self):
        for novel in self.novels:
			print '>>>', novel[0], novel[1]
			self.downloadNovel(novel[0], novel[1])

    def getRealContent(self, url):
        text = None
        for i in range(1,11):
            text = self.getHtmlContent(url)
            if text:
                break
            else:
                self.jjwxcapp.addLog("reconnect "+str(i)+': ')
                self.waitawhile()
            
        if not text:
            self.jjwxcapp.enableComponent()
            return None
        else:
            pattern = re.compile(r'<div class="noveltext">(.*?)</div>', re.S)
            match_obj = pattern.search(text)
            cleannoveltext = ''
            if match_obj:
                noveltext = match_obj.group(1)
                #print noveltext
                pattern = re.compile(r"<font color='#EEFAEE'>.*?</font>", re.S)
                # Replace string
                cleannoveltext = pattern.sub('',noveltext)
            #thread.start_new_thread ( testthread, (str(i)) )
            return cleannoveltext

    def getHtmlContent(self, url):
        text = None
        try:
            f = urlopen(url)
            text = f.read()
            f.close()
            self.jjwxcapp.addLog("  done!\n")
        except IOError, (errno, strerror):
            self.jjwxcapp.addLog("  %s!\n" % (strerror))

        return text

    def waitawhile(self):
        time.sleep(0)

    def writeChapterMenu(self, fd, novelurl, noveltitle):
        fd.write('<a name="menu">\n')
        fd.write('<h1 align="center">' + noveltitle + '</h1>\n')
        #fd.write('<div align="center"><a href="'+unicode(novelurl,'utf-8')+'">原文</a></div>\n')
        fd.write('<hr>\n')
        for chap in self.chaplist:
            fd.write('<ul><li>'+chap[0]+'. <a href="#'+chap[0]+'">'+chap[1]+'  '+chap[2]+'</a>'+'</li></ul>\n')
        fd.write('<hr>\n')
        fd.flush()
    
if __name__ == '__main__':
    app = model.Application(JJWXCArticleSys)
    app.MainLoop()
