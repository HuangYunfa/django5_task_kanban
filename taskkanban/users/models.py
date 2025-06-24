from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from PIL import Image
import os
import uuid
from datetime import datetime


def user_avatar_upload_path(instance, filename):
    """
    生成用户头像上传路径
    格式: avatars/user_{user_id}/{timestamp}_{uuid}.{ext}
    """
    # 获取文件扩展名
    ext = filename.split('.')[-1].lower()
    # 生成新的文件名: 时间戳_UUID
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_id = str(uuid.uuid4())[:8]
    new_filename = f"{timestamp}_{unique_id}.{ext}"
    # 返回完整路径
    return f"avatars/user_{instance.id or 'new'}/{new_filename}"


class User(AbstractUser):
    """
    扩展用户模型
    """
    # 基本信息
    email = models.EmailField(_('邮箱地址'), unique=True)
    phone = models.CharField(_('手机号码'), max_length=20, blank=True, null=True)
    avatar = models.ImageField(_('头像'), upload_to=user_avatar_upload_path, blank=True, null=True)
    
    # 个人信息
    nickname = models.CharField(_('昵称'), max_length=50, blank=True, null=True)
    bio = models.TextField(_('个人简介'), max_length=500, blank=True, null=True)
    location = models.CharField(_('所在地'), max_length=100, blank=True, null=True)
    website = models.URLField(_('个人网站'), blank=True, null=True)
    
    # 偏好设置
    language = models.CharField(
        _('语言偏好'),
        max_length=10,
        choices=[
            ('zh-hans', '简体中文'),
            ('zh-hant', '繁体中文'),
            ('en', 'English'),
        ],
        default='zh-hans',
    )
    timezone = models.CharField(
        _('时区'),
        max_length=50,
        default='Asia/Shanghai',
    )
    
    # 系统字段
    email_verified = models.BooleanField(_('邮箱已验证'), default=False)
    phone_verified = models.BooleanField(_('手机已验证'), default=False)
    last_login_ip = models.GenericIPAddressField(_('最后登录IP'), blank=True, null=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    # 设置邮箱为用户名字段
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        verbose_name = _('用户')
        verbose_name_plural = _('用户')
        db_table = 'users_user'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.nickname or self.username or self.email
    
    def get_display_name(self):
        """获取显示名称"""
        return self.nickname or self.get_full_name() or self.username
    
    def get_avatar_url(self):
        """获取头像URL"""
        if self.avatar and hasattr(self.avatar, 'url'):
            try:
                return self.avatar.url
            except (ValueError, OSError):
                # 如果头像文件不存在或损坏，返回默认头像
                return '/static/images/default-avatar.png'
        return '/static/images/default-avatar.png'
    
    def save(self, *args, **kwargs):
        # 如果是更新现有用户且头像发生变化，删除旧头像
        if self.pk:
            try:
                old_user = User.objects.get(pk=self.pk)
                if old_user.avatar and old_user.avatar != self.avatar:
                    # 删除旧头像文件
                    if os.path.isfile(old_user.avatar.path):
                        os.remove(old_user.avatar.path)
                        # 尝试删除空的用户头像目录
                        try:
                            avatar_dir = os.path.dirname(old_user.avatar.path)
                            if os.path.isdir(avatar_dir) and not os.listdir(avatar_dir):
                                os.rmdir(avatar_dir)
                        except:
                            pass
            except User.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
        
        # 处理头像缩放
        if self.avatar:
            try:
                img = Image.open(self.avatar.path)
                if img.height > 300 or img.width > 300:
                    output_size = (300, 300)
                    img.thumbnail(output_size)
                    img.save(self.avatar.path)
            except Exception:
                pass  # 忽略图片处理错误


class UserProfile(models.Model):
    """
    用户扩展资料模型
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # 职业信息
    job_title = models.CharField(_('职位'), max_length=100, blank=True, null=True)
    company = models.CharField(_('公司'), max_length=100, blank=True, null=True)
    department = models.CharField(_('部门'), max_length=100, blank=True, null=True)
    
    # 技能标签
    skills = models.JSONField(_('技能标签'), default=list, blank=True)
    
    # 通知设置
    email_notifications = models.BooleanField(_('邮件通知'), default=True)
    browser_notifications = models.BooleanField(_('浏览器通知'), default=True)
    mobile_notifications = models.BooleanField(_('手机通知'), default=True)
    
    # 隐私设置
    show_email = models.BooleanField(_('公开邮箱'), default=False)
    show_phone = models.BooleanField(_('公开手机'), default=False)
    
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('用户资料')
        verbose_name_plural = _('用户资料')
        db_table = 'users_profile'
    
    def __str__(self):
        return f"{self.user.get_display_name()} 的资料"
