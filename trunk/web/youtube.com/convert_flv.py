#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from threadpool import ThreadPool

def run_cmd(cmd):
    os.system(cmd)

def convertFlv2Mp4underDir(path):
    if not os.path.isdir(path):
        if existFile(path):
            print "  Path:["+ path+ "] is not a directory, exit!\n"
            return
        else:
            os.makedirs(path)
    pool = ThreadPool(6)
    
    CMD = '''D:\\Program\\tools\\ffmpeg.exe -i "%s" -vcodec mpeg4 -b 1200kb -mbd 2 -aic 2 -cmp 2 -subcmp 2 -acodec libfaac -ac 2 -ab 128000 -y "%s"'''
    for file_name in os.listdir(path):
        flv_path = path+'/'+file_name
        if os.path.isfile(flv_path):
        
            mp4_file_name = file_name[:file_name.rfind('.')]+'.mp4'
            mp4_save_path = path+'/mp4/'+mp4_file_name
            
            if os.path.exists(mp4_save_path):
                print "  File:[" + mp4_save_path+ "] already exists, pass.\n"
                continue
            cmd = CMD%(flv_path, mp4_save_path)
            print cmd
            
            pool.queueTask(run_cmd, (cmd))
            
    pool.joinAll()
    
#--------------------------------------------------------------------------------------
if __name__ == '__main__':
    convertFlv2Mp4underDir('D:\Develop\Others\code-of-ldmiao\web\youtube.com\youtube_videos')