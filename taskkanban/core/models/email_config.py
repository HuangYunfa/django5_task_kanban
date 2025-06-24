from django.db import models
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

class EmailConfiguration(models.Model):
    """邮件配置模型 - 从数据库动态读取邮件配置"""
    
    # 配置名称 - 可以支持多套邮件配置
    name = models.CharField(max_length=100, unique=True, default='default', 
                           verbose_name='配置名称')
    
    # SMTP服务器配置
    backend = models.CharField(max_length=200, 
                              default='django.core.mail.backends.smtp.EmailBackend',
                              verbose_name='邮件后端')
    host = models.CharField(max_length=100, verbose_name='SMTP服务器')
    port = models.IntegerField(default=587, verbose_name='SMTP端口')
    use_tls = models.BooleanField(default=True, verbose_name='使用TLS')
    use_ssl = models.BooleanField(default=False, verbose_name='使用SSL')
    
    # 认证信息 - 敏感信息
    username = models.CharField(max_length=200, verbose_name='用户名')
    password = models.CharField(max_length=200, verbose_name='密码')
    default_from_email = models.EmailField(verbose_name='默认发件人')
    
    # 配置状态
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    is_default = models.BooleanField(default=False, verbose_name='是否为默认配置')
    
    # 其他设置
    timeout = models.IntegerField(default=30, verbose_name='超时时间(秒)')
    ssl_certfile = models.CharField(max_length=200, blank=True, null=True, 
                                   verbose_name='SSL证书文件')
    ssl_keyfile = models.CharField(max_length=200, blank=True, null=True,
                                  verbose_name='SSL密钥文件')
    
    # 元数据
    description = models.TextField(blank=True, verbose_name='配置描述')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '邮件配置'
        verbose_name_plural = '邮件配置'
        db_table = 'email_configurations'
    
    def __str__(self):
        return f"{self.name} ({self.host}:{self.port})"
    
    def save(self, *args, **kwargs):
        # 如果设置为默认配置，取消其他默认配置
        if self.is_default:
            EmailConfiguration.objects.exclude(pk=self.pk).update(is_default=False)
        
        # 清除缓存
        cache.delete_many([
            'email_config_default',
            f'email_config_{self.name}',
            'active_email_configs'
        ])
        
        super().save(*args, **kwargs)
        logger.info(f"邮件配置已更新: {self.name}")
    
    def delete(self, *args, **kwargs):
        # 清除缓存
        cache.delete_many([
            'email_config_default',
            f'email_config_{self.name}',
            'active_email_configs'
        ])
        super().delete(*args, **kwargs)
    
    @classmethod
    def get_default_config(cls):
        """获取默认邮件配置"""
        config = cache.get('email_config_default')
        if config is None:
            try:
                config = cls.objects.filter(is_active=True, is_default=True).first()
                if not config:
                    # 如果没有默认配置，获取第一个激活的配置
                    config = cls.objects.filter(is_active=True).first()
                
                if config:
                    cache.set('email_config_default', config, 300)  # 缓存5分钟
                    logger.info(f"获取到默认邮件配置: {config.name}")
                else:
                    logger.warning("没有找到可用的邮件配置")
            except Exception as e:
                logger.error(f"获取默认邮件配置失败: {e}")
                config = None
        
        return config
    
    @classmethod
    def get_config_by_name(cls, name):
        """根据名称获取邮件配置"""
        cache_key = f'email_config_{name}'
        config = cache.get(cache_key)
        
        if config is None:
            try:
                config = cls.objects.filter(name=name, is_active=True).first()
                if config:
                    cache.set(cache_key, config, 300)  # 缓存5分钟
            except Exception as e:
                logger.error(f"获取邮件配置失败 [{name}]: {e}")
                config = None
        
        return config
    
    def to_django_settings(self):
        """转换为Django邮件设置格式"""
        return {
            'EMAIL_BACKEND': self.backend,
            'EMAIL_HOST': self.host,
            'EMAIL_PORT': self.port,
            'EMAIL_USE_TLS': self.use_tls,
            'EMAIL_USE_SSL': self.use_ssl,
            'EMAIL_HOST_USER': self.username,
            'EMAIL_HOST_PASSWORD': self.password,
            'DEFAULT_FROM_EMAIL': self.default_from_email,
            'SERVER_EMAIL': self.default_from_email,
            'EMAIL_TIMEOUT': self.timeout,
            'EMAIL_SSL_CERTFILE': self.ssl_certfile,
            'EMAIL_SSL_KEYFILE': self.ssl_keyfile,
        }
    
    def test_connection(self):
        """测试邮件配置连接"""
        try:
            from django.core.mail import get_connection
            from django.conf import settings
            
            # 临时设置邮件配置
            original_settings = {}
            config_dict = self.to_django_settings()
            
            for key, value in config_dict.items():
                if hasattr(settings, key):
                    original_settings[key] = getattr(settings, key)
                setattr(settings, key, value)
            
            try:
                connection = get_connection(
                    backend=self.backend,
                    host=self.host,
                    port=self.port,
                    username=self.username,
                    password=self.password,
                    use_tls=self.use_tls,
                    use_ssl=self.use_ssl,
                    timeout=self.timeout,
                )
                connection.open()
                connection.close()
                logger.info(f"邮件配置连接测试成功: {self.name}")
                return True, "连接测试成功"
                
            finally:
                # 恢复原始设置
                for key, value in original_settings.items():
                    setattr(settings, key, value)
                    
        except Exception as e:
            error_msg = f"连接测试失败: {str(e)}"
            logger.error(f"邮件配置连接测试失败 [{self.name}]: {e}")
            return False, error_msg
