#! /usr/bin/env python2.7
#coding=utf-8
import logging
import json
import sys
class JsonError:
    error={
        '1000':{
            'err':'unknown error',
            'c'  :'1000',
            'm'  :'error is not defined'
        },
        '1001':{
            'err':'Duplicated Username or Email!',
            'c'  :'1001',
            'm'  :'Please choose another uername(email)'
        },
        '1002':{
            'err':'Invalid username or password!',
            'c'  :'1002',
            'm'  :'Please check your username and password!'
        },
        '1003':{
            'err':'Token Expired',
            'c'  :'1003',
            'm'  :'Please authorize app. access privilege'
        },
        '1004':{
            'err':'No login Info.',
            'c'  :'1004',
            'm'  :'Please login!'
        },
        '1005':{
            'err':'No Token Info.',
            'c'  :'1005',
            'm'  :'Please Authorize app!'
        },
        '1007':{
            'err':'Can\'t fetch SNS status.',
            'c'  :'1007',
            'm'  :'Please post status!'
        }
    }

    def __init__(self,**wrargs):
        pass
    
    def e(self,**wrargs):
        print sys.argv[0]
        print sys.argv[1]
        if 'err' in wrargs:
            err=wrargs['err']
        else:
            err='unknown error'
        if 'c' in wrargs:
            c=wrargs['c']
        else:
            c='1000'
        if 'm' in wrargs:
            m=wrargs['m']
        else:
            m='error is not defined!'
        return json.loads('{"error":"%s","code":"%s","message":"%s"}'%(err,c,m))
    def default(self,code):
        d=self.error[code]
        err=d['err']
        c=d['c']
        m=d['m']
        return json.loads('{"error":"%s","code":"%s","message":"%s"}'%(err,c,m))
