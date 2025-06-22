#!/usr/bin/env python3
"""
API调试测试脚本
诊断具体的API问题
"""

import requests
import json

BASE_URL = 'http://127.0.0.1:8000'
API_URL = f'{BASE_URL}/api/v1'

def test_endpoint(url, method='GET', data=None, headers=None):
    """测试单个端点"""
    print(f"\n🔍 测试: {method} {url}")
    
    if headers is None:
        headers = {'Content-Type': 'application/json'}
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=headers)
        
        print(f"   状态码: {response.status_code}")
        print(f"   响应头: {dict(response.headers)}")
        
        # 尝试解析JSON响应
        try:
            json_data = response.json()
            print(f"   JSON响应: {json.dumps(json_data, indent=2, ensure_ascii=False)}")
        except:
            print(f"   文本响应: {response.text[:200]}...")
        
        return response
    except Exception as e:
        print(f"   错误: {e}")
        return None

def main():
    print("🔧 API调试测试")
    
    # 1. 测试API根端点（需要认证）
    test_endpoint(f"{API_URL}/")
    
    # 2. 测试文档端点（应该不需要认证）
    test_endpoint(f"{BASE_URL}/api/docs/")
      # 3. 测试用户创建端点（应该不需要认证）
    user_data = {
        'username': 'debuguser',
        'email': 'debug@example.com',
        'password': 'debugpass123',
        'password_confirm': 'debugpass123',
        'first_name': 'Debug',
        'last_name': 'User'
    }
    test_endpoint(f"{API_URL}/users/", 'POST', user_data)
      # 4. 测试JWT登录端点
    login_data = {
        'email': 'debug@example.com',  # 使用email而不是username
        'password': 'debugpass123'
    }
    response = test_endpoint(f"{BASE_URL}/api/auth/login/", 'POST', login_data)
    
    if response and response.status_code == 200:
        tokens = response.json()
        access_token = tokens.get('access')
        
        # 5. 使用token测试认证端点
        auth_headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
        test_endpoint(f"{API_URL}/", headers=auth_headers)
        test_endpoint(f"{API_URL}/users/me/", headers=auth_headers)

if __name__ == '__main__':
    main()
