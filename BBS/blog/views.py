import os
import json
import random
from io import BytesIO
from django.core.mail import send_mail
from django.shortcuts import render, redirect, reverse, HttpResponse
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import transaction
from django.db.models import F
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont
from blog import models
from blog import dataforms
from BBS import settings


# 主页
def index(request):
    articles = models.Article.objects.all()
    return render(request, 'index.html', {'article_list': articles})


# 验证码
# random_color是在settings里设置的变量
def random_color():
    return (
        random.randint(0, settings.random_color),
        random.randint(0, settings.random_color),
        random.randint(0, settings.random_color)
    )


def get_code(request):
    img = Image.new('RGB', (140, 34), color=random_color())
    img_draw = ImageDraw.Draw(img)
    font = ImageFont.truetype('static/font/ziti.TTF', size=25)
    random_code = ''
    for i in range(5):
        char_num = random.randint(0, 9)
        char_lower = chr(random.randint(97, 122))
        char_upper = chr(random.randint(65, 90))
        char_str = str(random.choice([char_num, char_lower, char_upper]))
        img_draw.text((i * 24 + 18, 0), char_str, random_color(), font=font)
        random_code += char_str
    request.session['valid_code'] = random_code
    # width = 140
    # height = 34
    # for i in range(10):
    #     x1 = random.randint(0, width)
    #     x2 = random.randint(0, width)
    #     y1 = random.randint(0, height)
    #     y2 = random.randint(0, height)
    # 在图片上画线
    # img_draw.line((x1, y1, x2, y2), fill=random_color())

    # for i in range(100):
    #     # # 画点
    #     img_draw.point([random.randint(0, width), random.randint(0, height)], fill=random_color())
    #     x = random.randint(0, width)
    #     y = random.randint(0, height)
    #     # 画弧形
    #     img_draw.arc((x, y, x + 4, y + 4), 0, 90, fill=random_color())

    f = BytesIO()
    img.save(f, 'png')
    data = f.getvalue()
    return HttpResponse(data)


# 登录
def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    elif request.is_ajax():
        # 登录完成后返回信息
        login_response = {'user': None, 'msg': None}
        # 获取ajax提交的name和pwd数据
        name = request.POST.get('name')
        pwd = request.POST.get('pwd')
        input_valid_code = request.POST.get('valid_code')
        print(input_valid_code)
        # 获取session中的valid_code
        if input_valid_code.upper() == request.session.get('valid_code').upper():
            # auth验证模块，进行登录用户验证
            user = auth.authenticate(request, username=name, password=pwd)
            if user:
                # 使用auth模块进行登录
                auth.login(request, user)
                login_response['user'] = name
                login_response['msg'] = '登陆成功'
                login_response['url'] = '/index/'
                print(login_response)
            else:
                login_response['msg'] = '用户名或密码错误'
        else:
            login_response['msg'] = '验证码错误'
        return JsonResponse(login_response)


# 注销
def logout(request):
    auth.logout(request)
    return redirect('/index/')


# 注册
def register(request):
    if request.method == 'GET':
        my_form = dataforms.UserRegForm()
        return render(request, 'register.html', {'my_form': my_form})
    elif request.is_ajax():
        response = {'status': 100, 'msg': None}
        print(request.POST)
        print(request.POST.get('username'))
        my_form = dataforms.UserRegForm(request.POST)
        if my_form.is_valid():
            dic = my_form.cleaned_data
            # 移除掉确认密码字段
            dic.pop('re_password')
            # 取出上传的文件对象
            my_file = request.FILES.get('my_file')
            # 如果上传的文件为空,这个字段不传,数据库里存默认值
            if my_file:
                # 放到字典中
                dic['avatar'] = my_file
            # 存数据的时候,多肯定不行,少,可以能行(null=True),它是可以的
            user = models.UserInfo.objects.create_user(**dic)
            '''
            models.FileField 有了这个字段,存文件,以及往数据库放文件路径,统统不需要自己做了
            只需要把文件对象赋给它就可以了
            '''
            print(user.username)
            # 注册成功后跳转的路径
            response['url'] = '/login/'
        else:
            # 返回错误信息
            response['status'] = 101
            response['msg'] = my_form.errors
        return JsonResponse(response)


# 注册校验
def check_username(request):
    response = {'status': 100, 'msg': None}
    name = request.POST.get('name')
    pwd = request.POST.get('pwd')
    user = models.UserInfo.objects.filter(username=name).first()
    if user:
        response['status'] = 101
        response['msg'] = '用户名已被占用,请重新输入'
    return JsonResponse(response)


# 后台管理
# @login_required(login_url='/login/')
def background_management(request):
    if request.method == 'GET':
        blog = request.user.blog
        article_list = models.Article.objects.filter(blog=blog)
        return render(request, 'background_management/m.html', {"article_list": article_list})


# 文章增删改查
def add_article(request):
    if request.method == 'GET':
        return render(request, 'background_management/add_article.html', )
    elif request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        soup = BeautifulSoup(content, 'html.parser')
        tags = soup.find_all()
        for tag in tags:
            if tag.name == 'script':
                tag.decompose()
        desc = soup.text[0:150]
        ret = models.Article.objects.create(title=title, desc=desc, content=str(soup), blog=request.user.blog)
        return redirect('/m/')


def delete_article(request):
    if request.method == 'GET':
        nid = request.GET.get('id')
        models.Article.objects.filter(nid=nid).delete()
        return redirect('/m/')


def update_article(request, pk)://使用有名分组
    if request.method == 'GET':
        article = models.Article.objects.get(pk=pk)
        print( article.title)
        print('----------------')
        return render(request, 'background_management/update_article.html', {'article': article})
    elif request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        soup = BeautifulSoup(content, 'html.parser')
        tags = soup.find_all()
        for tag in tags:
            if tag.name == 'script':
                tag.decompose()
        desc = soup.text[0:150]
        print(desc)
        ret = models.Article.objects.filter(nid=pk).update(title=title, desc=desc, content=str(soup),
                                                            blog=request.user.blog)
        print(ret)
        return redirect('/m/')


# 个人博客主页
def user_blog(request, username, *args, **kwargs):
    user = models.UserInfo.objects.filter(username=username).first()
    if not user:
        return render(request, 'error.html')
    blog = user.blog
    article_list = blog.article_set.all()
    condition = kwargs.get('condition')
    param = kwargs.get('param')
    if 'tag' == condition:
        article_list = article_list.filter(tag__pk=param)
    elif 'category' == condition:
        article_list = article_list.filter(category__pk=param)
    elif 'archive' == condition:
        archive_list = param.split('-')
        article_list = article_list.filter(create_time__year=archive_list[0], create_time__month=archive_list[1])
    return render(request, 'blog_site/user_blog.html', locals())


# 文章详情
def article_detail(request, username, id):
    username = username
    user = models.UserInfo.objects.filter(username=username).first()
    if not user:
        return render(request, 'error.html')
    blog = user.blog
    article = models.Article.objects.filter(pk=id).first()
    content_list = article.commit_set.all().order_by('pk')
    return render(request, 'blog_site/article_detail.html', locals())


# 点赞和点踩
def diggit(request):
    response = {'status': 100, 'msg': None}
    if request.user.is_authenticated():
        article_id = request.POST.get('article_id')
        is_up = request.POST.get('is_up')
        is_up = json.loads(is_up)
        user = request.user
        ret = models.UpAndDown.objects.filter(user_id=user.pk, article_id=article_id).exists()
        if ret:
            response['msg'] = '您已经点过了'
            response['status'] = 101
        else:
            with transaction.atomic():
                models.UpAndDown.objects.create(user=user, article_id=article_id, is_up=is_up)
                article = models.Article.objects.filter(pk=article_id)
                if is_up:
                    article.update(up_num=F('up_num') + 1)
                    response['msg'] = '点赞成功'
                else:
                    article.update(down_num=F('down_num') + 1)
                    response['msg'] = '反对成功'
    else:
        response['msg'] = '请先登录'
        response['status'] = 102
    return JsonResponse(response)


# 评论
def commit_content(request):
    response = {'status': 100, 'msg': None}
    if request.is_ajax():
        if request.user.is_authenticated():
            user = request.user
            article_id = request.POST.get('article_id')
            content = request.POST.get('content')
            pid = request.POST.get('pid')
            with transaction.atomic():
                ret = models.Commit.objects.create(user=user, article_id=article_id, content=content, parent_id=pid)
                models.Article.objects.filter(pk=article_id).update(commit_num=F('commit_num') + 1)
            response['msg'] = '评论成功'
            response['content'] = ret.content
            response['time'] = ret.create_time.strftime('%Y-%m-%d %X')
            response['user_name'] = ret.user.username
            if pid:
                response['parent_name'] = ret.parent.user.username
            from BBS import settings
            article_name = ret.article.title
            user_name = request.user.username
            from threading import Thread
            thread = Thread(target=send_mail, args=(
                '用户%s已经评论了%s文章' % (user_name, article_name), '评论内容如下:%s' % content, settings.EMAIL_HOST_USER,
                ['334147577@qq.com']))
            thread.start()
        else:
            response['status'] = 101
            response['msg'] = '您没有登录'
    else:
        response['status'] = 101
        response['msg'] = '您请求非法'
    return JsonResponse(response)


# 图片上传
def upload_img(request):
    print(request.FILES)
    uploadFile = request.FILES.get('uploadFile')
    path = os.path.join(settings.BASE_DIR, 'media', 'img')
    if not os.path.isdir(path):
        os.mkdir(path)
    file_path = os.path.join(path, uploadFile.name)
    with open(file_path, 'wb') as f:
        for line in uploadFile:
            f.write(line)
    dic = {
        'error': 0,
        'url': '/media/img/%s' % uploadFile.name,
    }
    return JsonResponse(dic)
