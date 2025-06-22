from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm, PasswordResetForm
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.db import models
from .models import User, UserProfile


class CustomUserCreationForm(UserCreationForm):
    """
    自定义用户注册表单
    """
    email = forms.EmailField(
        label=_('邮箱地址'),
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('请输入邮箱地址')
        })
    )
    nickname = forms.CharField(
        label=_('昵称'),
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('请输入昵称（可选）')
        })
    )
    password1 = forms.CharField(
        label=_('密码'),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('请输入密码')
        }),
    )
    password2 = forms.CharField(
        label=_('确认密码'),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('请再次输入密码')
        }),
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'nickname', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('请输入用户名')
            }),
        }
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError(_('该邮箱地址已被注册'))
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.nickname = self.cleaned_data['nickname']
        if commit:
            user.save()
        return user


class CustomLoginForm(AuthenticationForm):
    """
    自定义登录表单
    """
    username = forms.CharField(
        label=_('用户名或邮箱'),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('请输入用户名或邮箱')
        })
    )
    password = forms.CharField(
        label=_('密码'),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('请输入密码')
        }),
    )
    remember_me = forms.BooleanField(
        label=_('记住我'),
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if username is not None and password:
            # 尝试用用户名登录
            self.user_cache = authenticate(
                self.request, 
                username=username, 
                password=password
            )
            
            # 如果用户名登录失败，尝试用邮箱登录
            if self.user_cache is None:
                try:
                    user = User.objects.get(email=username)
                    self.user_cache = authenticate(
                        self.request,
                        username=user.username,
                        password=password
                    )
                except User.DoesNotExist:
                    pass
            
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)
        
        return self.cleaned_data


class UserProfileForm(forms.ModelForm):
    """
    用户资料编辑表单
    """
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'nickname', 'email', 
            'phone', 'bio', 'location', 'website', 'avatar',
            'language', 'timezone'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'nickname': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
            'language': forms.Select(attrs={'class': 'form-select'}),
            'timezone': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'first_name': _('名'),
            'last_name': _('姓'),
            'nickname': _('昵称'),
            'email': _('邮箱地址'),
            'phone': _('手机号码'),
            'bio': _('个人简介'),
            'location': _('所在地'),
            'website': _('个人网站'),
            'avatar': _('头像'),
            'language': _('语言偏好'),
            'timezone': _('时区'),
        }


class UserProfileExtendedForm(forms.ModelForm):
    """
    用户扩展资料表单
    """
    class Meta:
        model = UserProfile
        fields = [
            'job_title', 'company', 'department', 'skills',
            'email_notifications', 'browser_notifications', 'mobile_notifications',
            'show_email', 'show_phone'
        ]
        widgets = {
            'job_title': forms.TextInput(attrs={'class': 'form-control'}),
            'company': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'skills': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'placeholder': _('请输入技能标签，用逗号分隔')
            }),
            'email_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'browser_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'mobile_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_email': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_phone': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'job_title': _('职位'),
            'company': _('公司'),
            'department': _('部门'),
            'skills': _('技能标签'),
            'email_notifications': _('邮件通知'),
            'browser_notifications': _('浏览器通知'),
            'mobile_notifications': _('手机通知'),
            'show_email': _('公开邮箱'),
            'show_phone': _('公开手机'),
        }
    
    def clean_skills(self):
        """处理技能标签"""
        skills_text = self.cleaned_data.get('skills', '')
        if skills_text:
            # 将逗号分隔的字符串转换为列表
            skills_list = [skill.strip() for skill in skills_text.split(',') if skill.strip()]
            return skills_list
        return []


class CustomPasswordChangeForm(PasswordChangeForm):
    """
    自定义密码修改表单
    """
    old_password = forms.CharField(
        label=_('当前密码'),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('请输入当前密码')
        }),
    )
    new_password1 = forms.CharField(
        label=_('新密码'),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('请输入新密码')
        }),
    )
    new_password2 = forms.CharField(
        label=_('确认新密码'),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('请再次输入新密码')
        }),
    )


class CustomPasswordResetForm(PasswordResetForm):
    """
    自定义密码重置表单
    """
    email = forms.EmailField(
        label=_('邮箱地址'),
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('请输入注册时使用的邮箱地址')
        })
    )


class AvatarUploadForm(forms.ModelForm):
    """
    头像上传表单
    """
    class Meta:
        model = User
        fields = ['avatar']
        widgets = {
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
    
    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            # 检查文件大小（限制为5MB）
            if avatar.size > 5 * 1024 * 1024:
                raise ValidationError(_('头像文件大小不能超过5MB'))
            
            # 检查文件类型
            allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            if avatar.content_type not in allowed_types:
                raise ValidationError(_('头像文件格式不支持，请上传JPEG、PNG、GIF或WebP格式的图片'))
        
        return avatar


class UserSearchForm(forms.Form):
    """
    用户搜索表单
    """
    query = forms.CharField(
        label=_('搜索用户'),
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('输入用户名、昵称或邮箱进行搜索')
        })
    )
    
    def search_users(self):
        """执行用户搜索"""
        query = self.cleaned_data.get('query')
        if query:
            return User.objects.filter(
                models.Q(username__icontains=query) |
                models.Q(nickname__icontains=query) |
                models.Q(email__icontains=query) |
                models.Q(first_name__icontains=query) |
                models.Q(last_name__icontains=query)
            ).distinct()
        return User.objects.none()
