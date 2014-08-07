from django.contrib.auth.models import User
from happy365.models import Token,WeiboUser,WeiboStatus
from django.http import Http404
from django.db import IntegrityError
from django.contrib.auth import authenticate, login,logout
from django.views.decorators.csrf import csrf_exempt,ensure_csrf_cookie
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from happy365.serializers import UserSerializer,OAuthTokenSerializer
from happy365.messages import MessageWrapper
from happy365.weiboCrawel import ShowFetcher,StatusFetcher
import logging
import json
import datetime as dt
from django.utils import timezone
import pytz
from sys import path
import NLP
from ContentProvider import ContentProvider
from happy365.error import JsonError
logger=logging.getLogger(__name__)
je=JsonError()
cp=ContentProvider()
# Create your views here.
class UserView(APIView):
    def get_object(self,pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404
    def get(self,request,pk,format=None):
        user=self.get_object(pk)
        serializer=UserSerializer(user)
        return Response(serializer.data) 
    #update object
    def put(self,request,pk,format=None):
        user=self.get_object(pk)
        serializer=UserSerializer(user,data=request.DATA)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(je.e(err=serializer.errors,c='400',m='serializer.errors'),status=status.HTTP_400_BAD_REQUEST)
    #delete object
    def delete(self,request,pk,format=None):
        user=self.get_object(pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT) 
#sign in
class SignView(APIView):
    @method_decorator(ensure_csrf_cookie)
    def post(self,request,format=None):
        logger.info("logging SignView info...")
        logger.info(request.COOKIES)
        data=json.loads(json.dumps(request.DATA))
        logger.info('user:%s,email:%s' %(data['username'],data['email']))
        try:
            user=User.objects.create_user(username=data['username'],email=data['email'],password=data['password'])
        except IntegrityError,e:
            return Response(je.default('1001'),status=status.HTTP_400_BAD_REQUEST)
        logger.info("User creation success!")
        if user is not None:
            try:
                user.save()
            except IntegrityError,e:
                return Response(je.default('1001'),status=status.HTTP_400_BAD_REQUEST)
            user=authenticate(username=data['username'],password=data['password'])
            if user is not None:
                login(request,user)
                logger.info(request.user.id)
                serializer=UserSerializer(user)
                return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(je.default('1007'),status=status.HTTP_400_BAD_REQUEST)
#OAuth authorization
class OAuthChecker:
    def expired(self,auth_id):
        try:    
            token=Token.objects.get(user_id=auth_id)
        except:
            return None
        if token is not None:
            expire_time=token.expire_time
            now=dt.datetime.utcnow()
            utc=pytz.timezone("UTC")
            utc_now=utc.localize(now)
            logger.info("validate user %d's token, exp date:%s,cur date:%s" %\
(auth_id,expire_time.strftime("%Y-%m-%d-%H:%M"),\
utc_now.strftime("%Y-%m-%d-%H:%M")))
            
            if utc_now > expire_time:
                return True
            return False
        return True   

#login
class LoginView(APIView):
    def get(self,request):
        logger.info("Verify session validation.")
        user_id=request.user.id
        ret=None
        if user_id is  None:
            ret=False
        else:
            ret=True
        tp='{"login":"%s"}'
        m={True:"true",False:"false",None:"none"}
        result=json.loads(tp % m[ret])
        return Response(result,status=status.HTTP_200_OK)
    @method_decorator(ensure_csrf_cookie)
    def post(self,request,format=None):
        logger.info('logging Login View info...')
        logger.info("Session user is:%s" % request.user.id)
        logger.info(request.COOKIES)
        data=json.loads(json.dumps(request.DATA))
        username = data['username']
        password = data['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                serializer=UserSerializer(user)
                return Response(serializer.data,status=status.HTTP_200_OK)
            else:
                return Response(je.default('1002'),status=status.HTTP_400_BAD_REQUEST)
        else:
            # Return an 'invalid login' error message. 
            return Response(je.default('1002'),status=status.HTTP_400_BAD_REQUEST)
#token expired check view
class TokenValidator(APIView):
    def get(self,request,format=None):
        auth_uid=request.user.id
        if auth_uid is not None:
            ochecker=OAuthChecker()
            ret=ochecker.expired(auth_uid)
            access_token=None
            if ret ==False:
                token=Token.objects.get(user_id=auth_uid)
                access_token=token.access_token
            tp='{"expired":"%s","token":"%s"}'
            m={True:"true",False:"false",None:"none"}
            result=json.loads(tp % (m[ret],access_token))
            return Response(result,status=status.HTTP_200_OK)
        return Response(je.default('1002'),status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    def get(self,request,format=None):
        logger.info("Logout")
        logout(request)
        return Response(status=status.HTTP_200_OK)
class OAuthTokenView(APIView):
    #get token by pk
    def get_object(self,pk):
        try:
            return Token.objects.get(pk=pk)
        except Token.DoesNotExist:
            return Response(je.default('1004'),status=status.HTTP_400_BAD_REQUEST)
    #get token by weibo user id
    def get_object_by_uid(self,uid):
        try:
            return Token.objects.get(user_id=uid)
        except Token.DoesNotExist:
            return None
    def get(self,request,format=None):
        logger.info("redirect to this url")
        return Response(status=status.HTTP_200_OK)
    
    def delete(self,request,format=None):
        auth_uid=request.user.id
        if auth_uid is None:
            return Response(je.default('1004'),status=status.HTTP_400_BAD_REQUEST)
        token=self.get_object_by_uid(int(auth_uid))
        if token is not None:
            token.delete()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
        
    #create token
    @method_decorator(ensure_csrf_cookie)
    def post(self,request,format=None):
        logger.info("logging OAuthTokenView info.")
        logger.info(request.COOKIES)
        data=json.loads(json.dumps(request.DATA))
        logger.info(data)
        uid=data['uid']
        access_token=data['access_token']
        expire_in=data['expires_in']
        auth_uid=request.user.id
        logger.info("session user id:"+ str(auth_uid))
        #logger.info("uid:%s, token:%s, expire_in:%d" %(uid,access_token,int(expire_in)))
        if auth_uid is None:
            raise Http404
        create_time=dt.datetime.now()
        expire_time=create_time+dt.timedelta(seconds=int(expire_in))#to seconds
        #-----------------------------------------
        token=self.get_object_by_uid(int(auth_uid))
        if token is not None:
            token.access_token=access_token
            token.expire_in=int(expire_in)
            token.create_time=create_time
            token.expire_time=expire_time
            token.save()
        else:
            token=Token(user_id=auth_uid,weibo_uid=uid,\
access_token=access_token,expire_in=expire_in,\
create_time=create_time,expire_time=expire_time)
            token.save()
        return Response(status=status.HTTP_201_CREATED)
    #update token
    @method_decorator(ensure_csrf_cookie)
    def put(self,request,format=None):
        logger.info("Logging OAuthTokenView info.")
        data=json.loads(json.dumps(request.DATA))
        logger.info(data)
        uid=data['uid']
        access_token=data['access_token']
        expire_in=data['expires_in']
        auth_uid=request.user.id
        logger.info("Session user id:"+str( auth_uid))
        if auth_uid is None:
            raise Http404
        create_time=dt.datetime.now()
        expire_time=create_time+dt.timedelta(seconds=expire_in)
        token=self.get_object_by_uid(int(auth_uid))
        if token is None:
            logger.info("Token is None")
        token.delete()
        new_token=Token(id=token.id,user_id=auth_uid,\
weibo_uid=uid,access_token=access_token,expire_in=expire_in,\
create_time=create_time,expire_time=expire_time)
        new_token.save()
        return Response(status=status.HTTP_201_CREATED)

def get_token(auth_uid):
    try:
        token=Token.objects.get(user_id=auth_uid)
        return token
    except:
        logger.info("Get session user token failure")
    return None

def requestFilter(request):
    logger.info("Logging Request Filter Info")
    auth_uid=request.user.id
    if auth_uid is None:
        return '1004',None,None
    logger.info("Session user id is:%d." %auth_uid)
    token=get_token(auth_uid)
    if token is None:
        return '1005',None,None
    logger.info("Fetch token info success")
    if token is not None:
        uid=token.weibo_uid
        access_token=token.access_token
        ochecker=OAuthChecker()
        ret=ochecker.expired(auth_uid)
        if ret is True:
            return '1003',None,None
        return None,access_token,uid

#Fetch feeds
class Feeds(APIView):
    def get(self,request,format=None):
        logger.info("Logging Feeds Info")
        code,access_token,uid= requestFilter(request)
        if code is not None:
            return Response(je.default(code),status=status.HTTP_400_BAD_REQUEST)
        logger.info('Start to fetch user latest status')
        try:
            sf=StatusFetcher()
            result=sf.fetch(access_token=access_token,uid=uid,count='1')
            txt=result.next()
            logger.info('Status to analysis:'+txt)
            if txt is None:
                return Response(je.default('1006'),status=status.HTTP_400_BAD_REQUEST)
        except:
            logger.info('Fetch status failure')
        scores=NLP.sentiment(txt)
        try:
            body=cp.content(scores)
            return Response(body,status=status.HTTP_200_OK)
        except:
            return Response(je.default('1000'),status=status.HTTP_400_BAD_REQUEST)

class Profile(APIView):
    def get(self,request,format=None):
        logger.info("Logging profile Info")
        code,access_token,uid= requestFilter(request)
        if code is not None:
            return Response(je.default(code),status=status.HTTP_400_BAD_REQUEST)
        logger.info('Start to fetch user all status')
        sf=StatusFetcher()
        result=sf.fetch(access_token=access_token,uid=uid,count='200')
        #NLP.tf_idfs(result)
        tags=NLP.tags(result)
        for k in tags:
            logger.info(tags[k])
        return Response(status=status.HTTP_200_OK)
        #logger.info("Fetch profile failure")
        #return Response(status=status.HTTP_400_BAD_REQUEST)
