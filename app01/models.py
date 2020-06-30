from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
'''
先写普通
在写外键
'''

class UserInfo(AbstractUser):
    phone = models.BigIntegerField(verbose_name='手机号',null=True,blank=True)
    '''
    null=True 数据库该字段可以为空
    blank=True admin后台管理改字段可以为空
    '''
    #头像
    avatar = models.FileField(upload_to='avatar/',default='avatar/default.png')
    ceate_time = models.DateField(auto_now_add=True)

    blog = models.OneToOneField(to='Blog',null=True)

    class Meta:
        verbose_name_plural = '用户表'  #修改admin后台管理的表名

    def __str__(self):
        return self.username




class Blog(models.Model):
    site_name = models.CharField(verbose_name='站点名称',max_length=32)
    site_title = models.CharField(verbose_name='站点标题',max_length=32)
    site_theme = models.CharField(verbose_name='站点样式',max_length=64)
    class Meta:
        verbose_name_plural = '站点表'
    def __str__(self):
        return self.site_name



class Category(models.Model):
    name = models.CharField(verbose_name='文章分类',max_length=32)
    blog = models.ForeignKey(to='Blog',null=True)
    class Meta:
        verbose_name_plural = '文章分类表'

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(verbose_name='文章标签',max_length=32)
    blog = models.ForeignKey(to='Blog',null=True)
    class Meta:
        verbose_name_plural = '文章标签表'

    def __str__(self):
        return self.name

class Artice(models.Model):
    title = models.CharField(verbose_name='文章标题',max_length=64)
    desc = models.CharField(verbose_name='文章简介',max_length=255)
    content = models.TextField(verbose_name='文章内容')
    create_time = models.DateField(auto_now_add=True)
    #数据库优化
    up_num = models.BigIntegerField(default=0,verbose_name='点赞数')
    down_num = models.BigIntegerField(default=0,verbose_name='点踩数')
    comment_num = models.BigIntegerField(default=0,verbose_name='评论数')

    blog = models.ForeignKey(to='Blog', null=True)
    category = models.ForeignKey(to='Category',null=True)
    tags = models.ManyToManyField(to='Tag',through='Article2Tag',through_fields=('article','tag'))
    class Meta:
        verbose_name_plural = '文章表'
    def __str__(self):
        return self.title


class Article2Tag(models.Model):
    article = models.ForeignKey(to='Artice')
    tag = models.ForeignKey(to='Tag')
    class Meta:
        verbose_name_plural = '文章标签外键表'


class UpAndDown(models.Model):
    user = models.ForeignKey(to='UserInfo')
    artice = models.ForeignKey(to='Artice')
    is_up = models.BooleanField()
    class Meta:
        verbose_name_plural = '点赞点踩表'

class Comment(models.Model):
    user = models.ForeignKey(to='UserInfo')
    artice = models.ForeignKey(to='Artice')
    content = models.CharField(max_length=255,verbose_name='评论内容')
    comment_time = models.DateTimeField(auto_now_add=True)
    #自关联
    parent = models.ForeignKey(to='self',null=True)
    class Meta:
        verbose_name_plural = '评论表'






