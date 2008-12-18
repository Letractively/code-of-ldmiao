#!/usr/bin/env python
# -*- coding: utf-8 -*-

import youtube_downloader

if __name__=='__main__':
    url = 'http://www.youtube.com/results?search_query=Statistical+Aspects+of+Data+Mining&search_type=&aq=f'
    youtube_downloader.downloadAllVideos(url)
    