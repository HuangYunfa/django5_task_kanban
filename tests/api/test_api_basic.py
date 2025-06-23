#!/usr/bin/env python
"""
API功能测试脚本
测试RESTful API的核心功能
"""

import requests
import json
import sys
from requests.auth import HTTPBasicAuth

# API基础URL
BASE_URL = "http://127.0.0.1:8000/api"

class APITester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        
    def test_api_documentation(self):
        """测试API文档可访问性"""
        print("🔍 测试API文档...")
        
        endpoints = [
            f"{BASE_URL}/docs/",           # Swagger UI
            f"{BASE_URL}/redoc/",          # ReDoc
            f"{BASE_URL}/schema/",         # OpenAPI Schema
            f"{BASE_URL}/v1/",             # API Root
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(endpoint, timeout=10)
                if response.status_code == 200:
                    print(f"✅ {endpoint} - 可访问")
                else:
                    print(f"⚠️  {endpoint} - 状态码: {response.status_code}")
            except Exception as e:
                print(f"❌ {endpoint} - 错误: {e}")
    
    def test_user_registration(self):
        """测试用户注册"""
        print("\n👤 测试用户注册...")
        
        user_data = {
            "username": "testapi",
            "email": "testapi@example.com",
            "password": "testpassword123",
            "password_confirm": "testpassword123",
            "first_name": "Test",
            "last_name": "API"
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/v1/users/",
                json=user_data,
                timeout=10
            )
            
            if response.status_code == 201:
                print("✅ 用户注册成功")
                user_info = response.json()
                print(f"   用户ID: {user_info.get('id')}")
                print(f"   用户名: {user_info.get('username')}")
                return user_info
            else:
                print(f"❌ 用户注册失败 - 状态码: {response.status_code}")
                print(f"   错误详情: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ 用户注册异常: {e}")
            return None
    
    def test_jwt_authentication(self):
        """测试JWT认证"""
        print("\n🔐 测试JWT认证...")
        
        # 使用现有用户或admin用户进行测试
        auth_data = {
            "username": "admin",  # 假设有admin用户
            "password": "admin123"
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/auth/login/",
                json=auth_data,
                timeout=10
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get('access')
                print("✅ JWT认证成功")
                print(f"   Access Token: {self.access_token[:50]}...")
                
                # 设置默认认证头
                self.session.headers.update({
                    'Authorization': f'Bearer {self.access_token}'
                })
                return True
            else:
                print(f"❌ JWT认证失败 - 状态码: {response.status_code}")
                print(f"   错误详情: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ JWT认证异常: {e}")
            return False
    
    def test_user_me_endpoint(self):
        """测试当前用户信息端点"""
        print("\n🔍 测试当前用户信息...")
        
        if not self.access_token:
            print("❌ 没有有效的JWT令牌")
            return False
        
        try:
            response = self.session.get(
                f"{BASE_URL}/v1/users/me/",
                timeout=10
            )
            
            if response.status_code == 200:
                user_info = response.json()
                print("✅ 获取当前用户信息成功")
                print(f"   用户名: {user_info.get('username')}")
                print(f"   邮箱: {user_info.get('email')}")
                return True
            else:
                print(f"❌ 获取用户信息失败 - 状态码: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 获取用户信息异常: {e}")
            return False
    
    def test_tasks_endpoint(self):
        """测试任务API端点"""
        print("\n📋 测试任务API...")
        
        if not self.access_token:
            print("❌ 没有有效的JWT令牌")
            return False
        
        try:
            # 获取任务列表
            response = self.session.get(
                f"{BASE_URL}/v1/tasks/",
                timeout=10
            )
            
            if response.status_code == 200:
                tasks = response.json()
                print("✅ 获取任务列表成功")
                print(f"   任务数量: {len(tasks.get('results', []))}")
                return True
            else:
                print(f"❌ 获取任务列表失败 - 状态码: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 任务API测试异常: {e}")
            return False
    
    def test_api_pagination(self):
        """测试API分页"""
        print("\n📄 测试API分页...")
        
        if not self.access_token:
            print("❌ 没有有效的JWT令牌")
            return False
        
        try:
            response = self.session.get(
                f"{BASE_URL}/v1/users/?page=1&page_size=5",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ API分页测试成功")
                print(f"   总数: {data.get('count', 0)}")
                print(f"   当前页结果数: {len(data.get('results', []))}")
                return True
            else:
                print(f"❌ 分页测试失败 - 状态码: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 分页测试异常: {e}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 60)
        print("🚀 开始API功能测试")
        print("=" * 60)
        
        tests = [
            ("API文档", self.test_api_documentation),
            ("用户注册", self.test_user_registration),
            ("JWT认证", self.test_jwt_authentication),
            ("当前用户信息", self.test_user_me_endpoint),
            ("任务API", self.test_tasks_endpoint),
            ("API分页", self.test_api_pagination),
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed_tests += 1
            except Exception as e:
                print(f"❌ {test_name} 测试异常: {e}")
        
        print("\n" + "=" * 60)
        print(f"📊 测试完成: {passed_tests}/{total_tests} 通过")
        
        if passed_tests == total_tests:
            print("🎉 所有API测试通过！")
            return True
        else:
            print("⚠️  部分API测试失败，请检查日志")
            return False

def main():
    """主函数"""
    try:
        tester = APITester()
        success = tester.run_all_tests()
        
        print("\n" + "=" * 60)
        print("💡 API测试说明:")
        print("1. 访问 http://127.0.0.1:8000/api/docs/ 查看Swagger文档")
        print("2. 访问 http://127.0.0.1:8000/api/v1/ 查看API浏览界面")
        print("3. 使用JWT令牌进行认证")
        print("4. 所有API端点都支持分页")
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n用户中断测试")
        sys.exit(1)
    except Exception as e:
        print(f"测试脚本异常: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
