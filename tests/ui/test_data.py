"""
UI测试的测试数据
"""
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

@transaction.atomic
def create_test_user(username="project_manager", password="demo123456", is_staff=True, is_superuser=True):
    """创建测试用户"""
    if not User.objects.filter(username=username).exists():
        user = User.objects.create_user(
            username=username,
            password=password,
            email=f"{username}@example.com",
            is_staff=is_staff,
            is_superuser=is_superuser
        )
        return user
    return User.objects.get(username=username)
