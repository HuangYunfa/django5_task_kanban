"""
自定义SMTP邮件后端
基于用户提供的原始工作代码
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings


class CustomSMTPBackend(BaseEmailBackend):
    """
    自定义SMTP邮件后端
    使用与用户原始代码相同的逻辑
    """
    
    def __init__(self, host=None, port=None, username=None, password=None,
                 use_tls=None, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently)
        self.host = host or settings.EMAIL_HOST
        self.port = port or settings.EMAIL_PORT
        self.username = username or settings.EMAIL_HOST_USER
        self.password = password or settings.EMAIL_HOST_PASSWORD
        self.use_tls = use_tls if use_tls is not None else settings.EMAIL_USE_TLS
        
    def send_messages(self, email_messages):
        """
        发送邮件消息
        """
        if not email_messages:
            return 0
        
        sent_count = 0
        for message in email_messages:
            try:
                if self._send_single_message(message):
                    sent_count += 1
            except Exception as e:
                if not self.fail_silently:
                    raise e
                    
        return sent_count
    
    def _send_single_message(self, message):
        """
        发送单个邮件消息
        使用用户原始代码的逻辑
        """
        try:
            # 创建SMTP连接 - 按照用户原始代码
            smtp = smtplib.SMTP(self.host, self.port)
            
            # 启用TLS
            if self.use_tls:
                smtp.starttls()
            
            # 登录
            if self.username and self.password:
                smtp.login(self.username, self.password)
            
            # 构建邮件
            mime_message = self._build_mime_message(message)
            
            # 发送邮件
            smtp.sendmail(
                message.from_email,
                message.to,
                mime_message.as_string()
            )
            
            # 关闭连接
            smtp.quit()
            
            return True
            
        except Exception as e:
            print(f"邮件发送失败: {e}")
            if not self.fail_silently:
                raise e
            return False
      def _build_mime_message(self, message):
        """
        构建MIME邮件消息
        """
        # 如果有HTML内容，创建multipart消息
        if hasattr(message, 'alternatives') and message.alternatives:
            mime_message = MIMEMultipart('alternative')
            
            # 添加纯文本部分
            text_part = MIMEText(message.body, 'plain', 'utf-8')
            mime_message.attach(text_part)
            
            # 添加HTML部分
            for content, mimetype in message.alternatives:
                if mimetype == 'text/html':
                    html_part = MIMEText(content, 'html', 'utf-8')
                    mime_message.attach(html_part)
        else:
            # 只有纯文本
            mime_message = MIMEText(message.body, 'plain', 'utf-8')
        
        # 设置邮件头
        mime_message['Subject'] = message.subject
        mime_message['From'] = message.from_email
        mime_message['To'] = ', '.join(message.to)
        
        if message.cc:
            mime_message['Cc'] = ', '.join(message.cc)
        
        if message.bcc:
            mime_message['Bcc'] = ', '.join(message.bcc)
        
        return mime_message
