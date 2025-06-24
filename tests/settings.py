"""用于测试的Django设置"""
from taskkanban.settings import *

# 添加tests目录到PYTHONPATH
import sys
import os
TEST_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TEST_DIR)

# 添加tests目录到Django的app列表
INSTALLED_APPS += ['tests']

# 设置测试数据库
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
