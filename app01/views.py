from django.shortcuts import render, HttpResponse, redirect
from app01.myforms import MyRegForm
from django.http import JsonResponse
from app01 import models
from PIL import Image, ImageDraw, ImageFont
from bs4 import BeautifulSoup
from BBS import settings

"""
Image:生成图片
ImageDraw:能够在图片上乱涂乱画
ImageFont:控制字体样式
"""
from io import BytesIO, StringIO

"""
内存管理器模块
BytesIO:临时帮你存储数据 返回的时候数据是二进制
StringIO:临时帮你存储数据 返回的时候数据是字符串
"""
import random, uuid, os, json
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from utils import pagination
from django.db.models import Count, F
from django.db.models.functions import TruncMonth


# Create your views here.


def register(requester):
    form_obj = MyRegForm()
    if requester.method == 'POST':
        back_dic = {"code": 1000, 'msg': ''}
        # 校验数据是否合法
        form_obj = MyRegForm(requester.POST)
        # print(form_obj.cleaned_data) {'username': 'jason', 'password': '123', 'confirm_password': '123', 'email': '123@qq.com'}
        if form_obj.is_valid():
            # 将校验通过的数据字典赋值给一个变量
            clean_data = form_obj.cleaned_data
            # 将字典里面的confirm_password键值对删除
            clean_data.pop('confirm_password')
            # 用户头像
            file_obj = requester.FILES.get('avatar')
            # 针对用户头像一定要判断是否传值不能直接添加到字典里面去
            if file_obj:
                # 重命名文件名称 防止名称相同被替换
                file_obj.name = crop_image(file_obj)
                clean_data['avatar'] = file_obj
            # 直接操作数据库保存数据
            models.UserInfo.objects.create_user(**clean_data)
            back_dic['url'] = '/login/'
        else:
            back_dic['code'] = 2000
            back_dic['msg'] = form_obj.errors
        return JsonResponse(back_dic)
    return render(requester, 'register.html', locals())


def crop_image(file):
    ext = file.name.split('.')[-1]
    filename = '{}.{}'.format(uuid.uuid4().hex[:10], ext)
    return filename


def login(request):
    if request.method == 'POST':
        back_dic = {'code': 1000, 'msg': ''}
        username = request.POST.get('username')
        password = request.POST.get('password')
        code = request.POST.get('code')
        if request.session.get('code').upper() == code.upper():
            user_obj = auth.authenticate(request, username=username, password=password)
            if user_obj:
                auth.login(request, user_obj)
                back_dic['url'] = '/home/'
            else:
                back_dic['code'] = 2000
                back_dic['msg'] = '用户名或密码错误'
        else:
            back_dic['code'] = 3000
            back_dic['msg'] = '验证码错误'
        return JsonResponse(back_dic)
    return render(request, 'login.html')


def get_random():
    return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)


def get_code(request):
    # 推导步骤1:直接获取后端现成的图片二进制数据发送给前端
    # with open(r'static/img/111.jpg','rb') as f:
    #     data = f.read()
    # return HttpResponse(data)

    # 推导步骤2:利用pillow模块动态产生图片
    # img_obj = Image.new('RGB',(430,35),'green')
    # img_obj = Image.new('RGB',(430,35),get_random())
    # # 先将图片对象保存起来
    # with open('xxx.png','wb') as f:
    #     img_obj.save(f,'png')
    # # 再将图片对象读取出来
    # with open('xxx.png','rb') as f:
    #     data = f.read()
    # return HttpResponse(data)

    # 推导步骤3:文件存储繁琐IO操作效率低  借助于内存管理器模块
    # img_obj = Image.new('RGB', (430, 35), get_random())
    # io_obj = BytesIO()  # 生成一个内存管理器对象  你可以看成是文件句柄
    # img_obj.save(io_obj,'png')
    # return HttpResponse(io_obj.getvalue())  # 从内存管理器中读取二进制的图片数据返回给前端

    # 最终步骤
    img_obj = Image.new('RGB', (200, 35), get_random())
    img_draw = ImageDraw.Draw(img_obj)
    img_font = ImageFont.truetype('static/font/222.ttf', 30)
    # 随机验证码
    code = ''
    for i in range(5):
        random_upper = chr(random.randint(65, 90))
        random_lower = chr(random.randint(97, 122))
        random_int = str(random.randint(0, 9))
        # 从上面三个里面随机选择一个
        tmp = random.choice([random_upper, random_lower, random_int])
        # 将产生的随机字符串写入到图片上
        """
        为什么一个个写而不是生成好了之后再写
        因为一个个写能够控制每个字体的间隙 
        而生成好之后再写的话间隙就没法控制了
         """
        img_draw.text((i * 35, 0), tmp, get_random(), img_font)
        code += tmp
    print(code)
    # 随机验证码在登陆的视图函数里面需要用到 要比对 所以要找地方存起来并且其他视图函数也能拿到
    request.session['code'] = code
    io_obj = BytesIO()
    img_obj.save(io_obj, 'png')
    return HttpResponse(io_obj.getvalue())


# 分页器
def page(request, obj):
    current_page = request.GET.get('page', 1)
    all_count = obj.count()
    # 1 传值生成对象
    page_obj = pagination.Pagination(current_page=current_page, all_count=all_count)
    # 2 直接对总数据进行切片操作
    page_queryset = obj[page_obj.start:page_obj.end]
    return page_queryset


def home(request):
    article_queryset = models.Artice.objects.all()
    # page_queryset = page(request,article_queryset)
    current_page = request.GET.get('page', 1)
    all_count = article_queryset.count()
    # 1 传值生成对象
    page_obj = pagination.Pagination(current_page=current_page, all_count=all_count)
    # 2 直接对总数据进行切片操作
    page_queryset = article_queryset[page_obj.start:page_obj.end]
    return render(request, 'home.html', locals())


@login_required
def logout(request):
    auth.logout(request)
    return redirect('/home/')


@login_required
def set_password(request):
    back_dic = {'code': 1000, 'msg': ''}
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        if new_password == confirm_password:
            if request.user.check_password(old_password):
                request.user.set_password(new_password)
                request.user.save()
            else:
                back_dic['code'] = 1001
                back_dic['msg'] = '原密码错误'
        else:
            back_dic['code'] = 1002
            back_dic['msg'] = '两次密码输入不一致'
        return JsonResponse(back_dic)


def site(request, username, **kwargs):
    # 先效验用户对应的站点是否存在
    user_obj = models.UserInfo.objects.filter(username=username).first()
    if not user_obj:
        return render(request, 'errors.html')
    blog = user_obj.blog
    # 查询当前个人站点下的所有的文章
    article_list = models.Artice.objects.filter(blog=blog)
    if kwargs:
        # print(kwargs)  # {'condition': 'tag', 'param': '1'}
        condition = kwargs.get('condition')
        param = kwargs.get('param')
        # 判断用户到底想按照哪个条件筛选数据
        if condition == 'category':
            article_list = article_list.filter(category_id=param)
        elif condition == 'tag':
            article_list = article_list.filter(tags__id=param)
        else:
            year, month = param.split('-')  # 2020-11  [2020,11]
            article_list = article_list.filter(create_time__year=year, create_time__month=month)

    current_page = request.GET.get('page', 1)
    all_count = article_list.count()
    # 1 传值生成对象
    page_obj = pagination.Pagination(current_page=current_page, all_count=all_count)
    # 2 直接对总数据进行切片操作
    page_queryset = article_list[page_obj.start:page_obj.end]

    return render(request, 'site.html', locals())


def article_detail(request, username, article_id, **kwargs):
    user_obj = models.UserInfo.objects.filter(username=username).first()
    blog = user_obj.blog
    article_obj = models.Artice.objects.filter(id=article_id, blog__userinfo__username=username).first()
    if not article_id:
        return render(request, 'errors.html')
    # 获取文章所有评论的内容
    comment_list = models.Comment.objects.filter(artice=article_obj)
    return render(request, 'article.html', locals())


def up_or_down(request):
    if request.is_ajax():
        back_dic = {'code': 1000, 'msg': ''}
        # 1.校验用户是否登陆
        if request.user.is_authenticated():
            article_id = request.POST.get('article_id')
            is_up = json.loads(request.POST.get('is_up'))
            # 2.判断当前文章是否是当前用户自己写的(自己不能点自己的文章)
            article_obj = models.Artice.objects.filter(pk=article_id).first()
            usre_obj = article_obj.blog.userinfo
            if not usre_obj == request.user:
                # 3.当前用户是否已经给当前文章点过了
                is_click = models.UpAndDown.objects.filter(user=request.user, artice=article_obj)
                if not is_click:
                    # 操作数据库
                    if is_up:
                        # 点赞加一
                        models.Artice.objects.filter(pk=article_id).update(up_num=F('up_num') + 1)
                        back_dic['msg'] = '点赞成功'
                    else:
                        # 点踩加一
                        models.Artice.objects.filter(pk=article_id).update(down_num=F('down_num') + 1)
                        back_dic['msg'] = '点踩成功'
                    models.UpAndDown.objects.create(user=request.user, artice=article_obj, is_up=is_up)
                else:
                    back_dic['msg'] = '已经点过了'
                    back_dic['code'] = '1001'
            else:
                back_dic['msg'] = '不能帮自己点哦'
                back_dic['code'] = '1002'
        else:
            back_dic['msg'] = "请先<a href='/error.html/'>登入<a/>"
            back_dic['code'] = '1003'
        return JsonResponse(back_dic)


from django.db import transaction


def comment(request):
    # 自己也可以给自己的文章评论内容
    if request.is_ajax():
        back_dic = {'code': 1000, 'msg': ""}
        if request.method == 'POST':
            if request.user.is_authenticated():
                article_id = request.POST.get('article_id')
                content = request.POST.get("content")
                parent_id = request.POST.get('parent_id')
                # 直接操作评论表 存储数据      两张表
                with transaction.atomic():
                    models.Artice.objects.filter(pk=article_id).update(comment_num=F('comment_num') + 1)
                    models.Comment.objects.create(user=request.user, artice_id=article_id, content=content,
                                                  parent_id=parent_id)
                back_dic['msg'] = '评论成功'
            else:
                back_dic['code'] = 1001
                back_dic['msg'] = '用户未登陆'
            return JsonResponse(back_dic)


@login_required
def backend(request):
    # 获取当前用户所有的文章
    article_list = models.Artice.objects.filter(blog=request.user.blog)
    current_page = request.GET.get('page', 1)
    all_count = article_list.count()
    # 1 传值生成对象
    page_obj = pagination.Pagination(current_page=current_page, all_count=all_count)
    # 2 直接对总数据进行切片操作
    page_queryset = article_list[page_obj.start:page_obj.end]
    return render(request, 'backend/backend.html', locals())


@login_required
def add_article(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        category_id = request.POST.get('category')
        tag_list = request.POST.get('tag')

        # BeautifulSoup4模块使用:专门用来处理HTML中的内容
        soup = BeautifulSoup(content, 'html.parser')
        # 获取页面中的整个html
        tags = soup.find_all()
        # 获取所有的标签
        for tag in tags:
            # 针对script标签 直接删除
            # tag.name获取html中所有的标签
            if tag.name == 'script':
                # 删除标签
                tag.decompose()

        # 文章简介:截取文章中前150
        desc = soup.text[0:150]

        article_obj = models.Artice.objects.create(
            title=title,
            content=str(soup),
            desc=desc,
            category_id=category_id,
            blog=request.user.blog
        )

        # 文章和标签的关系表 是我们自己创建的 没法使用add set remove clear方法
        # 自己去操作关系表   一次性可能需要创建多条数据      批量插入bulk_create()
        article_obj_list = []
        for i in tag_list:
            tag_article_obj = models.Article2Tag(article=article_obj, tag_id=i)
            article_obj_list.append(tag_article_obj)
            # 批量插入数据
        models.Article2Tag.objects.bulk_create(article_obj_list)
        # 跳转到后台管理文章展示页
        return redirect('/backend/')

    category_list = models.Category.objects.filter(blog=request.user.blog)
    tag_list = models.Tag.objects.filter(blog=request.user.blog)
    return render(request, 'backend/add_article.html', locals())


def upload_image(request):
    back_dic = {'error': 0, }  # 先提前定义返回给编辑器的数据格式
    if request.method == "POST":
        # 获取用户上传的图片对象
        # print(request.FILES)  # 打印看到了健固定叫imgFile
        file_obj = request.FILES.get('imgFile')
        file_obj.name = crop_image(file_obj)
        # 手动拼接存储文件的路径
        file_dir = os.path.join(settings.BASE_DIR, 'media', 'article_img')
        # 优化操作 先判断当前文件夹是否存在 不存在 自动创建
        if not os.path.isdir(file_dir):
            os.mkdir(file_dir)  # 创建一层目录结构  article_img
        # 拼接图片的完整路径
        file_path = os.path.join(file_dir, file_obj.name)
        with open(file_path, 'wb') as f:
            for line in file_obj:
                f.write(line)
        back_dic['url'] = '/media/article_img/%s' % file_obj.name

    return JsonResponse(back_dic)

@login_required
def set_avatar(request):
    if request.method == 'POST':
        file_obj = request.FILES.get('avatar')
        # models.UserInfo.objects.filter(pk=request.user.pk).update(avatar=file_obj)  # 不会再自动加avatar前缀
        # 1.自己手动加前缀
        # 2.换一种更新方式
        file_obj.name = crop_image(file_obj)
        user_obj = request.user
        user_obj.avatar = file_obj
        user_obj.save()
        return redirect('/home/')
    blog = request.user.blog
    username = request.user.username
    return render(request,'set_avatar.html',locals())