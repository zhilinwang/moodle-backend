from rest_framework import serializers
from happy365.models import Token,WeiboUser,WeiboStatus
from django.contrib.auth.models import User
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=('id','username','email','first_name','last_name')

class OAuthTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model=Token
        fields=('id','user_id','weibo_uid','access_token','expire_in','create_time','expire_time')
   
