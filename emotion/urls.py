from django.conf.urls import patterns, include, url
from happy365 import views
from rest_framework.urlpatterns import format_suffix_patterns
#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'emotion.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^signup/$',views.SignView.as_view()),
    url(r'^signin/$',views.LoginView.as_view()),
    url(r'^vtoken/$',views.TokenValidator.as_view()),
    url(r'^logout/$',views.LogoutView.as_view()),
    url(r'^user/(?P<pk>[0-9]+)/$',views.UserView.as_view()),
    url(r'^token',views.OAuthTokenView.as_view()),
    url(r'^feed',views.Feeds.as_view()),
    url(r'^profile',views.Profile.as_view()),
    #url(r'^admin/', include(admin.site.urls)),
)
urlpatterns=format_suffix_patterns(urlpatterns)
