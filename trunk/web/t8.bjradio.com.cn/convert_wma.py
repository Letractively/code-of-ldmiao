#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from threadpool import ThreadPool

def run_cmd(cmds):
    for cmd in cmds:
        os.system(cmds)

def convertWMA2MP3underDir(path):
    if not os.path.isdir(path):
        if existFile(path):
            print "  Path:["+ path+ "] is not a directory, exit!\n"
            return
        else:
            os.makedirs(path)
    
    pool = ThreadPool(6)
    
    MP3_CMD = '''ffmpeg.exe -i "%s" -f mp3 "%s"'''
    DEL_CMD = '''del %s'''
    for file_name in os.listdir(path):
        wma_path = path+'\\'+file_name
        if os.path.isfile(wma_path) and wma_path.lower().endswith('.wma'):
            mp3_file_name = file_name[:file_name.rfind('.')]+'.mp3'
            mp3_save_path = path+'\\'+mp3_file_name
            if os.path.exists(mp3_save_path):
                print "  File:[" + mp3_save_path+ "] already exists, pass.\n"
            else:
                cmd1 = MP3_CMD%(wma_path, mp3_save_path)
                #cmd2 = DEL_CMD%(wma_path)
                print cmd1
                pool.queueTask(run_cmd, (cmd1))
        
    pool.joinAll()
    
#--------------------------------------------------------------------------------------
if __name__ == '__main__':
    convertWMA2MP3underDir('D:\\Develop\\Others\\code-of-ldmiao\\web\\t8.bjradio.com.cn')