from django.shortcuts import render, HttpResponse, reverse, redirect
from app01 import models


# Create your views here.
def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    elif request.method == 'POST':
        # print(request.POST)#<QueryDict: {'name': ['joke'], 'pwd': ['123']}>
        name = request.POST.get('name')
        pwd = request.POST.get('pwd')
        user = models.UserInfo.objects.filter(name=name, pwd=pwd)
        if user:
            return HttpResponse('登录成功')
        else:
            return HttpResponse('用户名或密码不存在')


def userlist(request):
    if request.method == 'GET':
        user_list = models.UserInfo.objects.all()
        return render(request, 'userlist.html', {'user_list': user_list})


def deleteuser(request):
    if request.method == 'GET':
        nid = request.GET.get('id')
        models.UserInfo.objects.filter(nid=nid).delete()
        return redirect('/userlist/')


def adduser(request):
    if request.method == 'GET':
        return render(request, 'adduser.html')
    elif request.method == 'POST':
        name = request.POST.get('name')
        pwd = request.POST.get('pwd')
        sex = request.POST.get('sex')
        phone = request.POST.get('phone')
        models.UserInfo.objects.create(name=name, pwd=pwd, sex=sex, phone=phone)
        return redirect('/userlist/')


def editeuser(request):
    if request.method == 'GET':
        id = request.GET.get('id')
        user = models.UserInfo.objects.filter(nid=id).first()
        return render(request, 'editeuser.html', {'user': user})
    elif request.method == 'POST':
        id=request.POST.get('id')
        name = request.POST.get('name')
        pwd = request.POST.get('pwd')
        sex = request.POST.get('sex')
        phone = request.POST.get('phone')
        models.UserInfo.objects.filter(nid=id).update(name=name, pwd=pwd, sex=sex, phone=phone)
        return redirect('/userlist/')
