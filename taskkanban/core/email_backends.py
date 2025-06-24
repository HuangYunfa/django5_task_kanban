"""
动态邮件后端 - 从数据库读取邮件配置
"""
from django.core.mail.backends.smtp import EmailBackend as SMTPEmailBackend
from django.core.mail.backends.console import EmailBackend as ConsoleEmailBackend
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class DatabaseConfigEmailBackend(SMTPEmailBackend):
    """从数据库读取配置的SMTP邮件后端"""
    
    def __init__(self, host=None, port=None, username=None, password=None,
                 use_tls=None, fail_silently=False, use_ssl=None, timeout=None,
                 ssl_keyfile=None, ssl_certfile=None, **kwargs):
        
        # 尝试从数据库获取配置
        config = self._get_email_config()
        
        if config:
            # 使用数据库配置
            host = host or config.host
            port = port or config.port
            username = username or config.username
            password = password or config.password
            use_tls = use_tls if use_tls is not None else config.use_tls
            use_ssl = use_ssl if use_ssl is not None else config.use_ssl
            timeout = timeout or config.timeout
            ssl_keyfile = ssl_keyfile or config.ssl_keyfile
            ssl_certfile = ssl_certfile or config.ssl_certfile
            
            logger.info(f"使用数据库邮件配置: {config.name}")
        else:
            # 回退到环境变量配置
            host = host or getattr(settings, 'EMAIL_HOST', 'localhost')
            port = port or getattr(settings, 'EMAIL_PORT', 25)
            username = username or getattr(settings, 'EMAIL_HOST_USER', '')
            password = password or getattr(settings, 'EMAIL_HOST_PASSWORD', '')
            use_tls = use_tls if use_tls is not None else getattr(settings, 'EMAIL_USE_TLS', False)
            use_ssl = use_ssl if use_ssl is not None else getattr(settings, 'EMAIL_USE_SSL', False)
            timeout = timeout or getattr(settings, 'EMAIL_TIMEOUT', None)
            ssl_keyfile = ssl_keyfile or getattr(settings, 'EMAIL_SSL_KEYFILE', None)
            ssl_certfile = ssl_certfile or getattr(settings, 'EMAIL_SSL_CERTFILE', None)
            
            logger.warning("未找到数据库邮件配置，使用默认设置")
        
        super().__init__(
            host=host, port=port, username=username, password=password,
            use_tls=use_tls, fail_silently=fail_silently, use_ssl=use_ssl,
            timeout=timeout, ssl_keyfile=ssl_keyfile, ssl_certfile=ssl_certfile,
            **kwargs
        )
    
    def _get_email_config(self):
        """从数据库获取邮件配置"""
        try:
            # 延迟导入避免循环依赖
            from core.models import EmailConfiguration
            return EmailConfiguration.get_default_config()
        except Exception as e:
            logger.error(f"获取数据库邮件配置失败: {e}")
            return None

class FlexibleEmailBackend:
    """灵活的邮件后端 - 可以根据配置选择不同的后端"""
    
    def __init__(self, **kwargs):
        self.backend = self._get_backend(**kwargs)
    
    def _get_backend(self, **kwargs):
        """根据配置选择邮件后端"""
        try:
            # 从数据库获取配置
            from core.models import EmailConfiguration
            config = EmailConfiguration.get_default_config()
            
            if config and config.backend:
                backend_class = config.backend
            else:
                # 回退到设置中的后端
                backend_class = getattr(settings, 'EMAIL_BACKEND', 
                                      'django.core.mail.backends.smtp.EmailBackend')
            
            # 动态导入后端类
            module_path, class_name = backend_class.rsplit('.', 1)
            module = __import__(module_path, fromlist=[class_name])
            backend_cls = getattr(module, class_name)
            
            return backend_cls(**kwargs)
            
        except Exception as e:
            logger.error(f"创建邮件后端失败: {e}")
            # 回退到控制台后端
            return ConsoleEmailBackend(**kwargs)
    
    def send_messages(self, email_messages):
        """发送邮件"""
        return self.backend.send_messages(email_messages)
    
    def open(self):
        """打开连接"""
        if hasattr(self.backend, 'open'):
            return self.backend.open()
        return False
    
    def close(self):
        """关闭连接"""
        if hasattr(self.backend, 'close'):
            self.backend.close()

# 为了向后兼容，提供别名
CustomSMTPEmailBackend = DatabaseConfigEmailBackend
