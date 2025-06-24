"""
自定义邮件后端，基于用户原始的成功代码
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class CustomSMTPEmailBackend(BaseEmailBackend):
    """
    自定义SMTP邮件后端，使用与用户原始代码相同的方式
    """
    
    def __init__(self, host=None, port=None, username=None, password=None,
                 use_tls=None, fail_silently=False, use_ssl=None, timeout=None,
                 ssl_keyfile=None, ssl_certfile=None, **kwargs):
        super().__init__(fail_silently=fail_silently)
        self.host = host or settings.EMAIL_HOST
        self.port = port or settings.EMAIL_PORT
        self.username = username or settings.EMAIL_HOST_USER
        self.password = password or settings.EMAIL_HOST_PASSWORD
        self.use_tls = use_tls if use_tls is not None else getattr(settings, 'EMAIL_USE_TLS', False)
        self.timeout = timeout or getattr(settings, 'EMAIL_TIMEOUT', None)
        self.connection = None
        
    def open(self):
        """打开SMTP连接"""
        if self.connection:
            return False
        
        try:
            # 使用与用户原始代码相同的方式
            self.connection = smtplib.SMTP(self.host, self.port)
            if self.use_tls:
                self.connection.starttls()
            if self.username and self.password:
                self.connection.login(self.username, self.password)
            return True
        except Exception as e:
            if not self.fail_silently:
                logger.error(f"SMTP连接失败: {e}")
                raise
            return False
    
    def close(self):
        """关闭SMTP连接"""
        if self.connection:
            try:
                self.connection.quit()
            except:
                pass
            finally:
                self.connection = None
    
    def send_messages(self, email_messages):
        """发送邮件消息"""
        if not email_messages:
            return 0
        
        new_conn_created = self.open()
        if not self.connection:
            return 0
        
        num_sent = 0
        for message in email_messages:
            sent = self._send(message)
            if sent:
                num_sent += 1
        
        if new_conn_created:
            self.close()
        
        return num_sent
    
    def _send(self, email_message):
        """发送单个邮件"""
        if not self.connection:
            return False
        
        try:
            # 创建MIME消息
            if email_message.alternatives:
                # 有HTML版本，创建multipart消息
                mime_message = MIMEMultipart('alternative')
                
                # 添加纯文本版本
                text_part = MIMEText(email_message.body, 'plain', 'utf-8')
                mime_message.attach(text_part)
                
                # 添加HTML版本
                for content, mimetype in email_message.alternatives:
                    if mimetype == 'text/html':
                        html_part = MIMEText(content, 'html', 'utf-8')
                        mime_message.attach(html_part)
            else:
                # 只有纯文本
                mime_message = MIMEText(email_message.body, 'plain', 'utf-8')
            
            # 设置邮件头
            mime_message['Subject'] = email_message.subject
            mime_message['From'] = email_message.from_email
            mime_message['To'] = ', '.join(email_message.to)
            
            if email_message.cc:
                mime_message['Cc'] = ', '.join(email_message.cc)
            
            # 所有收件人
            recipients = email_message.to + email_message.cc + email_message.bcc
            
            # 使用与用户原始代码相同的方式发送
            self.connection.sendmail(
                email_message.from_email,
                recipients,
                mime_message.as_string()
            )
            
            logger.info(f"邮件发送成功: {email_message.subject} -> {recipients}")
            return True
            
        except Exception as e:
            logger.error(f"邮件发送失败: {e}")
            if not self.fail_silently:
                raise
            return False
