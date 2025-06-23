"""
API测试的特定配置和fixtures
"""
import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def api_client():
    """创建API测试客户端"""
    return APIClient()

@pytest.fixture
def authenticated_api_client():
    """创建已认证的API测试客户端"""
    client = APIClient()
    user = User.objects.create_user(
        username="api_test_user",
        password="api_test_password",
        email="api_test@example.com"
    )
    client.force_authenticate(user=user)
    return client, user
