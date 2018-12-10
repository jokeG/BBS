from django import forms
from django.forms import widgets
from django.core.exceptions import ValidationError
from blog import models


class UserRegForm(forms.Form):
    username = forms.CharField(max_length=18, min_length=3, label='请输入用户名',
                               widget=widgets.TextInput(attrs={'class': 'form-control'}),
                               error_messages={"min_length": "输入过短，最少4个字符", "max_length": "输入过长，最多4个字符",
                                               "required": "必填"}, required=True)
    password = forms.CharField(max_length=18, min_length=3, label='请输入密码',
                               widget=widgets.PasswordInput(attrs={'class': 'form-control'}),
                               error_messages={"min_length": "输入过短，最少5个字符", "required": "必填"}, required=True)
    re_password = forms.CharField(max_length=18, min_length=3, label='请再次输入密码',
                                  widget=widgets.PasswordInput(attrs={'class': 'form-control'}),
                                  error_messages={"min_length": "输入过短，最少5个字符", "required": "必填"}, required=True)
    email = forms.EmailField(max_length=18, min_length=3, label='请输入邮箱',
                             widget=widgets.TextInput(attrs={'class': 'form-control'}),
                             error_messages={"min_length": "输入过短，最少5个字符", "required": "必填"}, required=True)

    # 局部钩子函数
    def clean_username(self):
        name = self.cleaned_data.get('username')
        user = models.UserInfo.objects.filter(username=name).first()
        if user:
            raise ValidationError('用户名已存在,请重新输入')
        return name

    # 全局钩子函数
    def clean(self):
        pwd = self.cleaned_data.get('password')
        re_pwd = self.cleaned_data.get('re_password')
        if pwd == re_pwd:
            return self.cleaned_data
        else:
            raise ValidationError('两次密码不一致,请从新输入')
