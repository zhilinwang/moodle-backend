from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class WeiboUser(models.Model):
    user=models.ForeignKey(User,verbose_name="related user")
    uid=models.BigIntegerField()
    screenName=models.CharField(max_length=100)
    name=models.CharField(max_length=20)
    descp=models.CharField(max_length=140)
    location=models.CharField(max_length=100)
    url=models.CharField(max_length=100)
    domain=models.CharField(max_length=100)
    gender=models.CharField(max_length=1)
    onlineStatus=models.BooleanField()
    json=models.TextField()

class Token(models.Model):
    user=models.ForeignKey(User,verbose_name="related user")
    weibo_uid=models.BigIntegerField()
    access_token=models.CharField(max_length=200)
    expire_in=models.BigIntegerField()
    create_time=models.DateTimeField()
    expire_time=models.DateTimeField()


class WeiboStatus(models.Model):
    sid=models.BigIntegerField()
    text=models.CharField(max_length=500)
    weiboUserId=models.BigIntegerField()
    json=models.TextField()  

class Feeds(models.Model):
    pass 
