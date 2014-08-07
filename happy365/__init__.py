#! /usr/lib/enb python2.7
#coding=utf-8
import sys
import logging
logger=logging.getLogger(__name__)
def __init__():
        sys.path.append('/root/moodevaluator/main/server/senti-analysis/sentiment')
        sys.path.append('/root/moodevaluator/main/server/content-provider')
        logger.info(sys.path)
__init__()

