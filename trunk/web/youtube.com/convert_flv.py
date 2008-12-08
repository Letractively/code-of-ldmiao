#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

def convertFlv2Mp4underDir(path):
    if not os.path.isdir(path):
        if existFile(path):
            print "  Path:["+ path+ "] is not a directory, exit!\n"
            return
        else:
            os.makedirs(path)
    CMD = '''D:\Program\tools\ffmpeg.exe -i "%s" -vcodec libx264 -s 320x240 -r 20 -g 250 -keyint_min 25 -coder ac -me_range 16 -subq 5 -sc_threshold 40 -acodec libfaac -ab 96000 -ar 22500 -cmp +chroma -partitions +parti4x4+partp8x8+partb8x8 -i_qfactor 0.71 -b_strategy 1 -crf 30 -y "%s"'''
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
            os.system(cmd)
        
    
#--------------------------------------------------------------------------------------
if __name__ == '__main__':
    convertFlv2Mp4underDir('D:\Develop\Others\code-of-ldmiao\web\youtube.com\youtube_videos')