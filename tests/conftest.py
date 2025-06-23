"""
全局测试配置和pytest fixtures
"""
import os
import sys
import pytest
from django.conf import settings

# 确保测试可以找到项目模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# UI测试标记
def pytest_configure(config):
    """注册自定义标记"""
    config.addinivalue_line("markers", "ui: 标记为UI测试")
    config.addinivalue_line("markers", "api: 标记为API测试")
    config.addinivalue_line("markers", "slow: 标记为较慢的测试")
    config.addinivalue_line("markers", "integration: 标记为集成测试")

@pytest.fixture(scope="session")
def django_db_setup():
    """配置测试数据库"""
    settings.DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }

@pytest.fixture
def authenticated_client(client, django_user_model):
    """创建已认证的测试客户端"""
    username = "testuser"
    password = "testpassword"
    user = django_user_model.objects.create_user(username=username, password=password)
    client.login(username=username, password=password)
    return client, user
