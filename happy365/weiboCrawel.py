#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib2
import urllib
import logging
import json
import simplejson as sj
import datetime as dt
from django.db import Error,IntegrityError
from happy365.models import WeiboStatus,WeiboUser
BASE='https://api.weibo.com/2/'
STATUS={'show':'statuses/user_timeline.json'}
logger=logging.getLogger(__name__)
class Crawler:
    def crawl(self,url,method,**kwargs):
        body=''
        if method=='GET':
            param=None
            if len(kwargs) >0 :
                param='?'
                lst=[]
                for key in kwargs:
                   lst.append(key+'='+str(kwargs[key]))
                param+='&'.join(lst)
            full_url=url.rstrip('/')
            full_url=full_url+param
            logger.info(full_url)
            try:
                req=urllib2.Request(full_url)
                response=urllib2.urlopen(req)
                body=response.read()
                logger.info(body)
            except urllib2.HTTPError,e:
                logger.error(e.code)
                logger.error(e.read())
            return body
        if method=='POST':
            param={}
            if len(kwargs) >0:
                param=json.loads(json.dumps(kwargs))
                logger.info(param)
            try:
                #todo
                logger.info('logging todo')
            except urllib2.HTTPError,e:
                logger.error(e.code)
                logger.error(e.read())
            return body    
            
class StatusFetcher:
    def __save__(self,uid,status):
        text=status['text']
        #logger.info("Text to save:%s" % text)
        weiboStatus=WeiboStatus(sid=status['id'],text=text,weiboUserId=uid,json=status)
        try:
            weiboStatus.save()
        except (Error,IntegrityError),e:
            logger.error(e)
        logger.info("weibo status's text is:%s" % weiboStatus.text)
        return weiboStatus.text
    def fetch(self,access_token,uid,count):
        url='https://api.weibo.com/2/statuses/user_timeline.json' 
        crawler=Crawler()
        body=crawler.crawl(url,'GET',access_token=access_token,uid=uid,count=count)
        if body is not None:
            d=json.loads(body)
            #logger.info("Weibo status:%s" % d)
            statuses=d['statuses']
            logger.info("Statuses count:%d" % len(statuses))
            for s in statuses:
                tx=self.__save__(uid,s)
                yield(tx)
class ShowFetcher:
    def fetch(self,access_token,uid):
        url='https://api.weibo.com/2/users/show.json'
        crawler=Crawler()
        body=crawler.crawl(url,'GET',access_token=access_token,uid=uid)
        logger.info(body)
        #todo:save weibo user infomation into db model.
