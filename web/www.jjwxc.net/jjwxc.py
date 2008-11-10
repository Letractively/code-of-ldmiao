#!/usr/bin/python
# -*- coding:  utf-8-*-
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

class PrintDot(Thread):
    jjwxcapp = None
    def __init__(self, jjwxcapp):
        Thread.__init__(self)
        self.jjwxcapp = jjwxcapp
    def run(self):
        while 1:
            self.jjwxcapp.addLog('>')
            time.sleep(1)

class NovelProcess(Thread):
    savedir = None
    novels = None
    chaplist = None
    jjwxcapp = None
    pDotThread = None
    
    def __init__(self, jjwxcapp, novelurls, savedir):
        Thread.__init__(self)
        self.jjwxcapp = jjwxcapp
        self.savedir = savedir
        pattern = re.compile(r"""(http://www.jjwxc.net/onebook.php\?novelid=\d{1,})\s*""", re.IGNORECASE| re.DOTALL)
        self.novels = pattern.findall(novelurls)
        self.pDotThread = PrintDot(self.jjwxcapp)

    def run(self):
        self.process()
    
    def getTotalChapterNum(self, url):
        noveltitle = None
        self.jjwxcapp.addLog('[Novel index] ['+ time.strftime("%X") +'] ' + url +'\n')
        self.jjwxcapp.addLog(' └→Connect...   ')
        text = None
        for i in range(1,11):
            text = self.getHtmlContent(url)
            if text:
                break
            else:
                self.jjwxcapp.addLog(" └→Reconnect "+str(i)+': ')
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
            chapnum = 0
            if len(self.chaplist)>=1:
                chapnum = int(self.chaplist[len(self.chaplist)-1][0])

            self.jjwxcapp.displayStatus( 1/float(chapnum+1) )
            return (chapnum, noveltitle)

    def downloadNovel(self, novelurl):
        noveltitle = None
        chapnum, noveltitle = self.getTotalChapterNum(novelurl)
        if chapnum <=0:
            return
            
       #替换Windows文件名不允许的字符
        novelfilename = noveltitle.replace('?','？')
        novelfilename = novelfilename.replace('\\','＼')
        novelfilename = novelfilename.replace('/','／')
        novelfilename = novelfilename.replace(':','∶')
        novelfilename = novelfilename.replace('*','※')
        novelfilename = novelfilename.replace('"','＂')
        novelfilename = novelfilename.replace('>','〉')
        novelfilename = novelfilename.replace('<','〈')
        novelfilename = novelfilename.replace('|','｜')
        
        savefile = toiso(self.savedir) + '\\' + novelfilename + '.htm'
        
        print savefile
        

        fd = open(savefile,'w')
        
        fd.write('<head><title>' + noveltitle + '</title></head>\n')
        fd.write('<body bgcolor="#EEFAEE">');
        
        self.writeChapterMenu(fd, novelurl, noveltitle)

        downloadchapcount = 0;
        for chap in self.chaplist:
            i = int(chap[0])
            self.jjwxcapp.addLog('['+str(i)+'/'+str(chapnum)+'] ['+ time.strftime("%X") +'] ' + novelurl + '&chapterid=' + str(i) +'\n')
            #self.jjwxcapp.addLog(' └→' + self.chaplist[i-1][1] + ' ' + self.chaplist[i-1][2] + '\n' )
            self.jjwxcapp.addLog(' └→Connect...   ')

            chapurl = novelurl + '&chapterid=' + str(i)
            
            cleannoveltext = self.getRealContent(chapurl)
            #print cleannoveltext
            
            fd.write('<a name="'+str(i)+'">\n')
            fd.write(cleannoveltext)
            fd.write('<div align="right"><a href="#menu">回目录</a></div>\n')
            fd.write('<hr>\n')
            fd.flush()
            if i < chapnum:
                self.waitawhile()
            downloadchapcount = downloadchapcount + 1
            self.jjwxcapp.displayStatus((i+1)/float(chapnum+1))
        
        fd.write('</body>');
        fd.close()

        #for chap in self.chaplist:
        #    self.jjwxcapp.addLog(chap[0]+'\t'+chap[1]+'\t'+chap[2]+'\n')

        self.jjwxcapp.addLog('\nNovel download successful, total ' + str(chapnum) + ' chapters.'+'\n\n\n')
        #self.jjwxcapp.addLog('Save to dir: '+self.savedir+'\n')
        
    def process(self):
        #disable the componenets while downloading
        self.jjwxcapp.disableComponent()
        
        for novel in self.novels:
            #print '>>>', novel
            self.jjwxcapp.displayStatus(0)
            self.downloadNovel(novel)
        
        #enable the componenets after downloading successfully
        self.jjwxcapp.enableComponent()

    def getRealContent(self, url):
        text = None
        for i in range(1,11):
            text = self.getHtmlContent(url)
            if text:
                break
            else:
                self.jjwxcapp.addLog(" └→Reconnect "+str(i)+': ')
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
        #if not self.pDotThread.isAlive():
        #	self.pDotThread.start()
        try:
            f = urlopen(url)
            text = f.read()
            f.close()
            self.jjwxcapp.addLog("  done!\n")

        except IOError, (errno, strerror):
            self.jjwxcapp.addLog("  %s!\n" % (strerror))
        #self.pDotThread.suspend()
        
        return text

    def waitawhile(self):
        time.sleep(0)

    def writeChapterMenu(self, fd, novelurl, noveltitle):
        fd.write('<a name="menu">\n')
        fd.write('<h1 align="center">' + noveltitle + '</h1>\n')
        fd.write('<div align="center"><a href="' + toiso(novelurl) + '">原文</a></div>\n' )
        fd.write('<hr>\n')
        for chap in self.chaplist:
            fd.write('<ul><li>'+chap[0]+'. <a href="#'+chap[0]+'">'+chap[1]+'  '+chap[2]+'</a>'+'</li></ul>\n')
        fd.write('<hr>\n')
        fd.flush()

def toiso(s):
    if isinstance(s, unicode):
        return s.encode("iso-8859-1")
    else:
        return s


if __name__ == '__main__':
    app = model.Application(JJWXCArticleSys)
    app.MainLoop()
