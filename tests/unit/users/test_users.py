"""
用户模块测试
测试用户认证、注册、登录等功能
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail
from django.contrib.messages import get_messages

User = get_user_model()


class UserAuthenticationTestCase(TestCase):
    """用户认证测试"""
    
    def setUp(self):
        self.client = Client()
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': '测试',
            'last_name': '用户',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
        }
        
    def test_user_registration(self):
        """测试用户注册"""
        url = reverse('users:register')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # 测试注册表单提交
        response = self.client.post(url, self.user_data)
        self.assertEqual(response.status_code, 302)  # 重定向到登录页面
        
        # 验证用户已创建
        user = User.objects.get(username='testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.first_name, '测试')
        self.assertEqual(user.last_name, '用户')
        
    def test_user_login(self):
        """测试用户登录"""
        # 先创建用户
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        
        url = reverse('users:login')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # 测试登录
        login_data = {
            'username': 'testuser',
            'password': 'testpassword123',
        }
        response = self.client.post(url, login_data)
        self.assertEqual(response.status_code, 302)  # 重定向到首页
        
        # 验证用户已登录
        user = User.objects.get(username='testuser')
        self.assertTrue('_auth_user_id' in self.client.session)
        
    def test_user_logout(self):
        """测试用户登出"""
        # 先创建并登录用户
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.client.login(username='testuser', password='testpassword123')
        
        # 测试登出
        url = reverse('users:logout')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)  # 重定向到登录页面
        
        # 验证用户已登出
        self.assertFalse('_auth_user_id' in self.client.session)
        
    def test_password_reset_request(self):
        """测试密码重置请求"""
        # 创建用户
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        
        url = reverse('users:password_reset')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # 提交密码重置请求
        response = self.client.post(url, {'email': 'test@example.com'})
        self.assertEqual(response.status_code, 302)  # 重定向到完成页面
        
        # 验证邮件已发送
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('重置您的密码', mail.outbox[0].subject)
        
    def test_user_profile_access(self):
        """测试用户资料页面访问"""
        # 创建并登录用户
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.client.login(username='testuser', password='testpassword123')
        
        url = reverse('users:profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')        
    def test_user_profile_update(self):
        """测试用户资料更新"""
        # 创建并登录用户
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.client.login(username='testuser', password='testpassword123')
        
        url = reverse('users:profile')
        update_data = {
            'first_name': '更新的',
            'last_name': '名字',
            'email': 'updated@example.com',
            'language': 'zh-hans',
            'timezone': 'Asia/Shanghai',
        }
        response = self.client.post(url, update_data)
        self.assertEqual(response.status_code, 302)  # 重定向
        
        # 验证更新成功
        user.refresh_from_db()
        self.assertEqual(user.first_name, '更新的')
        self.assertEqual(user.last_name, '名字')
        self.assertEqual(user.email, 'updated@example.com')
        
    def test_password_change(self):
        """测试密码修改"""
        # 创建并登录用户
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='oldpassword123'
        )
        self.client.login(username='testuser', password='oldpassword123')
        
        url = reverse('users:password_change')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # 提交密码修改
        change_data = {
            'old_password': 'oldpassword123',
            'new_password1': 'newpassword123',
            'new_password2': 'newpassword123',
        }
        response = self.client.post(url, change_data)
        self.assertEqual(response.status_code, 302)  # 重定向到完成页面
        
        # 验证密码已更改
        user.refresh_from_db()
        self.assertTrue(user.check_password('newpassword123'))
        
    def test_unauthenticated_access(self):
        """测试未认证用户访问受保护页面"""
        url = reverse('users:profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # 重定向到登录页面
        
        # 验证重定向到登录页面
        expected_url = f"{reverse('users:login')}?next={url}"
        self.assertRedirects(response, expected_url)


class UserModelTestCase(TestCase):
    """用户模型测试"""
    
    def test_user_creation(self):
        """测试用户创建"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123',
            first_name='测试',
            last_name='用户'
        )
        
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.first_name, '测试')
        self.assertEqual(user.last_name, '用户')
        self.assertTrue(user.check_password('testpassword123'))
        self.assertFalse(user.email_verified)
        
    def test_user_str_method(self):
        """测试用户字符串表示"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.assertEqual(str(user), 'testuser')
        
    def test_user_display_name(self):
        """测试用户显示名称"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123',
            first_name='测试',
            last_name='用户'        )
        
        self.assertEqual(user.get_display_name(), '测试 用户')
        
        # 测试没有姓名时的显示名称
        user.first_name = ''
        user.last_name = ''
        user.save()
        self.assertEqual(user.get_display_name(), 'testuser')
        
    def test_user_avatar_url(self):
        """测试用户头像URL"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        
        # 测试默认头像
        avatar_url = user.get_avatar_url()
        self.assertIsNotNone(avatar_url)
        # 应该是默认头像路径
        self.assertEqual(avatar_url, '/static/images/default-avatar.svg')


class UserFormsTestCase(TestCase):
    """用户表单测试"""
    
    def test_user_registration_form_valid(self):
        """测试有效的注册表单"""
        from users.forms import CustomUserCreationForm
        
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': '测试',
            'last_name': '用户',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
        
    def test_user_registration_form_invalid(self):
        """测试无效的注册表单"""
        from users.forms import CustomUserCreationForm
        
        # 密码不匹配
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': '测试',
            'last_name': '用户',
            'password1': 'testpassword123',
            'password2': 'differentpassword',
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        
        # 用户名重复
        User.objects.create_user(username='testuser', email='existing@example.com')
        form_data['password2'] = 'testpassword123'
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        
    def test_user_login_form_valid(self):
        """测试有效的登录表单"""
        from users.forms import CustomLoginForm
        
        # 先创建用户
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        
        form_data = {
            'username': 'testuser',
            'password': 'testpassword123',
        }
        form = CustomLoginForm(data=form_data)
        self.assertTrue(form.is_valid())
        
    def test_user_login_form_invalid(self):
        """测试无效的登录表单"""
        from users.forms import CustomLoginForm
        
        form_data = {
            'username': 'nonexistent',
            'password': 'wrongpassword',
        }
        form = CustomLoginForm(data=form_data)
        self.assertFalse(form.is_valid())
