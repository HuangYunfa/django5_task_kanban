import os
from celery import Celery

# 设置默认Django设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskkanban.settings.local')

# 创建Celery实例
app = Celery('taskkanban')
app.config_from_object('django.conf:settings', namespace='CELERY')

# 加载任务模块
app.autodiscover_tasks()

# 使用Django的settings.py配置Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现任务
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
