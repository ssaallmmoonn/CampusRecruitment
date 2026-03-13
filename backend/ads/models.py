from django.db import models
from users.models import Company

class Banner(models.Model):
    title = models.CharField(max_length=100, verbose_name='标题')
    image = models.ImageField(upload_to='banners/', verbose_name='图片')
    link_url = models.URLField(verbose_name='链接地址', blank=True, null=True)
    order = models.PositiveIntegerField(default=0, verbose_name='排序')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '轮播图'
        verbose_name_plural = verbose_name
        ordering = ['order', '-create_time']

    def __str__(self):
        return self.title

class Brand(models.Model):
    name = models.CharField(max_length=100, verbose_name='品牌名称')
    logo = models.ImageField(upload_to='brands/', verbose_name='品牌Logo', blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='关联企业')
    order = models.PositiveIntegerField(default=0, verbose_name='排序')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '品牌专区'
        verbose_name_plural = verbose_name
        ordering = ['order', '-create_time']

    def __str__(self):
        return self.name
