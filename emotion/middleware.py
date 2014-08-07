import re
from django import http
from django.middleware.csrf import get_token
import logging
logger=logging.getLogger(__name__)
class CsrftokenMiddleware:
    m={'GET','HEAD','OPTIONS','TRACE'}
    def process_response(self, request, response):
        logger.info(__name__)
        if request.method not in self.m:
            try:
                csrftoken=get_token(request)
                response['csrftoken']=csrftoken
                logger.info(csrftoken)
            except:
                logger.info('Fetch csrftoken failure!')
        return response
