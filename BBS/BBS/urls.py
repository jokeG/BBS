"""BBS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.views.static import serve
from blog import views
from BBS import settings

urlpatterns = [
    url(r'^$', views.index),
    url(r'^admin/', admin.site.urls),
    url(r'^index/', views.index),
    url(r'^login/', views.login),
    url(r'^logout/', views.logout),
    url(r'^get_code/', views.get_code),
    url(r'^check_username/', views.check_username),
    url(r'^register/', views.register),
    # 后台管理
    url(r'^m/', views.background_management),
    url(r'^add_article/', views.add_article),
    url(r'^update_article/(?P<pk>\d+)', views.update_article),
    url(r'^delete_article/', views.delete_article),


    url(r'^media/(?P<path>.*)', serve, {'document_root': settings.MEDIA_ROOT}),
    # 点赞评论
    url(r'^diggit/', views.diggit),
    url(r'^commit_content/$', views.commit_content),
    url(r'^upload_img/', views.upload_img),

    url(r'^(?P<username>[\w]+)/(?P<condition>category|tag|archive)/(?P<param>.*)', views.user_blog),
    url(r'^(?P<username>[\w]+)/article/(?P<id>\d+)', views.article_detail),

    url(r'^(?P<username>[\w]+)$', views.user_blog),

]
