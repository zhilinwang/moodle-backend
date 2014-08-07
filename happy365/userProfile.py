#! /usr/bin/env python2.7
# coding=utf-8
from weiboCrawel import StatusFetcher
sf=StatusFetcher()
class userProfile:
    def __init__(self):
        pass
    def profile(self,access_token,uid):
        statuses=sf.fetch(access_token=access_token,uid=uid)
        
                
