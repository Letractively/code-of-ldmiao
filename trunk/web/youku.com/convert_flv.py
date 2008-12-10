#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from threadpool import ThreadPool

def run_cmd(cmd):
    os.system(cmd)

def convertFlv2Mp4underDir(path):
    if not os.path.isdir(path):
        if os.path.exists(path):
            print "  Path:["+ path+ "] is not a directory, exit!\n"
            return
        else:
            os.makedirs(path)
    
    pool = ThreadPool(6)
    
    MP4_CMD = '''D:\\Program\\tools\\ffmpeg.exe -i "%s" -vcodec mpeg4 -b 1200kb -mbd 2 -aic 2 -cmp 2 -subcmp 2 -acodec libfaac -ac 2 -ab 128000 -y "%s"'''
    MP3_CMD = '''D:\\Program\\tools\\ffmpeg.exe -i "%s" -vn -ar 44100 -ac 2 -ab 64 -f mp3 "%s"'''
    for file_name in os.listdir(path):
        flv_path = path+'/'+file_name
        if os.path.isfile(flv_path):
            mp4_file_name = file_name[:file_name.rfind('.')]+'.mp4'
            mp4_save_path = path+'\\mp4\\'+mp4_file_name
            if os.path.exists(mp4_save_path):
                print "  File:[" + mp4_save_path+ "] already exists, pass.\n"
            else:
                cmd = MP4_CMD%(flv_path, mp4_save_path)
                print cmd
                pool.queueTask(run_cmd, (cmd))
            
            mp3_file_name = file_name[:file_name.rfind('.')]+'.mp3'
            mp3_save_path = path+'\\mp3\\'+mp3_file_name
            if os.path.exists(mp3_save_path):
                print "  File:[" + mp3_save_path+ "] already exists, pass.\n"
            else:
                cmd = MP3_CMD%(flv_path, mp3_save_path)
                print cmd
                pool.queueTask(run_cmd, (cmd))
            
    pool.joinAll()
    
#--------------------------------------------------------------------------------------
if __name__ == '__main__':
    convertFlv2Mp4underDir('D:\\Develop\\Others\\code-of-ldmiao\\web\\youku.com\\videos')