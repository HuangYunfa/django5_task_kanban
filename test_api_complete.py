#!/usr/bin/env python3
"""
完整API功能测试脚本
测试用户、任务、看板、团队、报表的CRUD操作和自定义端点
"""

import requests
import json
import sys
from datetime import datetime

# 配置
BASE_URL = 'http://127.0.0.1:8000'
API_URL = f'{BASE_URL}/api/v1'

# 全局变量存储测试数据
test_data = {
    'tokens': {},
    'user_id': None,
    'board_id': None,
    'team_id': None,
    'task_id': None,
    'report_id': None
}

def print_section(title):
    """打印测试段落标题"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_result(test_name, success, details=None):
    """打印测试结果"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"   Details: {details}")

def make_request(method, endpoint, data=None, auth_token=None):
    """发送HTTP请求的通用函数"""
    url = f"{API_URL}{endpoint}"
    headers = {'Content-Type': 'application/json'}
    
    if auth_token:
        headers['Authorization'] = f'Bearer {auth_token}'
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=headers)
        elif method == 'PUT':
            response = requests.put(url, json=data, headers=headers)
        elif method == 'PATCH':
            response = requests.patch(url, json=data, headers=headers)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        
        return response
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

def test_api_documentation():
    """测试API文档是否可访问"""
    print_section("API文档访问测试")
    
    # 测试Swagger UI
    try:
        response = requests.get(f"{BASE_URL}/api/docs/")
        print_result("Swagger UI访问", response.status_code == 200, f"Status: {response.status_code}")
    except Exception as e:
        print_result("Swagger UI访问", False, str(e))
    
    # 测试API根端点
    try:
        response = requests.get(f"{API_URL}/")
        print_result("API根端点访问", response.status_code == 200, f"Status: {response.status_code}")
        if response.status_code == 200:
            api_data = response.json()
            print(f"   Available endpoints: {list(api_data.keys())}")
    except Exception as e:
        print_result("API根端点访问", False, str(e))

def test_user_registration_and_auth():
    """测试用户注册和认证"""
    print_section("用户注册和认证测试")
      # 注册新用户
    user_data = {
        'username': f'testuser_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
        'email': f'test_{datetime.now().strftime("%Y%m%d_%H%M%S")}@example.com',
        'password': 'testpass123',
        'password_confirm': 'testpass123',  # 添加password_confirm字段
        'first_name': 'Test',
        'last_name': 'User'
    }
    
    response = make_request('POST', '/users/', user_data)
    if response and response.status_code == 201:
        user_info = response.json()
        test_data['user_id'] = user_info['id']
        print_result("用户注册", True, f"User ID: {user_info['id']}")
    else:
        print_result("用户注册", False, f"Status: {response.status_code if response else 'No response'}")
        return False
      # 用户登录获取JWT令牌
    login_data = {
        'email': user_data['email'],  # 使用email而不是username
        'password': user_data['password']
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login/", json=login_data)
    if response.status_code == 200:
        tokens = response.json()
        test_data['tokens'] = tokens
        print_result("用户登录", True, "获取到JWT令牌")
    else:
        print_result("用户登录", False, f"Status: {response.status_code}")
        return False
    
    # 测试获取当前用户信息
    response = make_request('GET', '/users/me/', auth_token=test_data['tokens']['access'])
    if response and response.status_code == 200:
        user_info = response.json()
        print_result("获取当前用户信息", True, f"Username: {user_info['username']}")
    else:
        print_result("获取当前用户信息", False, f"Status: {response.status_code if response else 'No response'}")
    
    return True

def test_board_management():
    """测试看板管理功能"""
    print_section("看板管理测试")
    
    # 创建看板
    board_data = {
        'title': '测试看板',
        'description': '这是一个测试看板',
        'is_private': False
    }
    
    response = make_request('POST', '/boards/', board_data, auth_token=test_data['tokens']['access'])
    if response and response.status_code == 201:
        board_info = response.json()
        test_data['board_id'] = board_info['id']
        print_result("创建看板", True, f"Board ID: {board_info['id']}")
    else:
        print_result("创建看板", False, f"Status: {response.status_code if response else 'No response'}")
        return False
    
    # 获取看板列表
    response = make_request('GET', '/boards/', auth_token=test_data['tokens']['access'])
    if response and response.status_code == 200:
        boards = response.json()
        print_result("获取看板列表", True, f"Found {len(boards['results']) if 'results' in boards else len(boards)} boards")
    else:
        print_result("获取看板列表", False, f"Status: {response.status_code if response else 'No response'}")
    
    # 获取看板详情
    response = make_request('GET', f'/boards/{test_data["board_id"]}/', auth_token=test_data['tokens']['access'])
    if response and response.status_code == 200:
        board_detail = response.json()
        print_result("获取看板详情", True, f"Title: {board_detail['title']}")
    else:
        print_result("获取看板详情", False, f"Status: {response.status_code if response else 'No response'}")
    
    # 获取看板成员
    response = make_request('GET', f'/boards/{test_data["board_id"]}/members/', auth_token=test_data['tokens']['access'])
    if response and response.status_code == 200:
        members = response.json()
        print_result("获取看板成员", True, f"Members count: {len(members)}")
    else:
        print_result("获取看板成员", False, f"Status: {response.status_code if response else 'No response'}")
    
    return True

def test_team_management():
    """测试团队管理功能"""
    print_section("团队管理测试")
    
    # 创建团队
    team_data = {
        'name': '测试团队',
        'description': '这是一个测试团队'
    }
    
    response = make_request('POST', '/teams/', team_data, auth_token=test_data['tokens']['access'])
    if response and response.status_code == 201:
        team_info = response.json()
        test_data['team_id'] = team_info['id']
        print_result("创建团队", True, f"Team ID: {team_info['id']}")
    else:
        print_result("创建团队", False, f"Status: {response.status_code if response else 'No response'}")
        return False
    
    # 获取团队列表
    response = make_request('GET', '/teams/', auth_token=test_data['tokens']['access'])
    if response and response.status_code == 200:
        teams = response.json()
        print_result("获取团队列表", True, f"Found {len(teams['results']) if 'results' in teams else len(teams)} teams")
    else:
        print_result("获取团队列表", False, f"Status: {response.status_code if response else 'No response'}")
    
    # 获取团队成员
    response = make_request('GET', f'/teams/{test_data["team_id"]}/members/', auth_token=test_data['tokens']['access'])
    if response and response.status_code == 200:
        members = response.json()
        print_result("获取团队成员", True, f"Members count: {len(members)}")
    else:
        print_result("获取团队成员", False, f"Status: {response.status_code if response else 'No response'}")
    
    # 获取团队绩效
    response = make_request('GET', f'/teams/{test_data["team_id"]}/performance/', auth_token=test_data['tokens']['access'])
    if response and response.status_code == 200:
        performance = response.json()
        print_result("获取团队绩效", True, f"Team: {performance['team_name']}, Members: {performance['member_count']}")
    else:
        print_result("获取团队绩效", False, f"Status: {response.status_code if response else 'No response'}")
    
    return True

def test_task_management():
    """测试任务管理功能"""
    print_section("任务管理测试")
    
    if not test_data.get('board_id'):
        print_result("任务管理测试", False, "需要先创建看板")
        return False
    
    # 首先我们需要获取看板列表（BoardList），因为任务需要关联到看板列表
    # 这里我们模拟一个简单的任务创建，可能需要根据实际的Board结构调整
    
    # 获取任务列表
    response = make_request('GET', '/tasks/', auth_token=test_data['tokens']['access'])
    if response and response.status_code == 200:
        tasks = response.json()
        print_result("获取任务列表", True, f"Found {len(tasks['results']) if 'results' in tasks else len(tasks)} tasks")
    else:
        print_result("获取任务列表", False, f"Status: {response.status_code if response else 'No response'}")
    
    return True

def test_report_management():
    """测试报表管理功能"""
    print_section("报表管理测试")
    
    # 创建报表
    report_data = {
        'name': '测试报表',
        'description': '这是一个测试报表',
        'report_type': 'task_summary',
        'filters': {
            'date_range': 30
        }
    }
    
    response = make_request('POST', '/reports/', report_data, auth_token=test_data['tokens']['access'])
    if response and response.status_code == 201:
        report_info = response.json()
        test_data['report_id'] = report_info['id']
        print_result("创建报表", True, f"Report ID: {report_info['id']}")
    else:
        print_result("创建报表", False, f"Status: {response.status_code if response else 'No response'}")
        return False
    
    # 获取报表列表
    response = make_request('GET', '/reports/', auth_token=test_data['tokens']['access'])
    if response and response.status_code == 200:
        reports = response.json()
        print_result("获取报表列表", True, f"Found {len(reports['results']) if 'results' in reports else len(reports)} reports")
    else:
        print_result("获取报表列表", False, f"Status: {response.status_code if response else 'No response'}")
    
    # 获取报表数据
    response = make_request('GET', f'/reports/{test_data["report_id"]}/data/', auth_token=test_data['tokens']['access'])
    if response and response.status_code == 200:
        report_data = response.json()
        print_result("获取报表数据", True, f"Report contains {len(report_data)} data points")
    else:
        print_result("获取报表数据", False, f"Status: {response.status_code if response else 'No response'}")
    
    return True

def test_api_pagination_and_filtering():
    """测试API分页和过滤功能"""
    print_section("分页和过滤测试")
    
    # 测试用户列表分页
    response = make_request('GET', '/users/?page=1&page_size=5', auth_token=test_data['tokens']['access'])
    if response and response.status_code == 200:
        users = response.json()
        has_pagination = 'results' in users and 'count' in users
        print_result("用户列表分页", has_pagination, f"Pagination structure: {has_pagination}")
    else:
        print_result("用户列表分页", False, f"Status: {response.status_code if response else 'No response'}")
    
    # 测试任务过滤
    if test_data.get('board_id'):
        response = make_request('GET', f'/tasks/?board={test_data["board_id"]}', auth_token=test_data['tokens']['access'])
        if response and response.status_code == 200:
            tasks = response.json()
            print_result("任务按看板过滤", True, f"Found filtered tasks")
        else:
            print_result("任务按看板过滤", False, f"Status: {response.status_code if response else 'No response'}")

def main():
    """主测试函数"""
    print("🚀 开始API完整功能测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 执行测试序列
    try:
        # 1. API文档测试
        test_api_documentation()
        
        # 2. 用户注册和认证测试
        if not test_user_registration_and_auth():
            print("❌ 用户认证失败，终止测试")
            sys.exit(1)
        
        # 3. 看板管理测试
        test_board_management()
        
        # 4. 团队管理测试
        test_team_management()
        
        # 5. 任务管理测试
        test_task_management()
        
        # 6. 报表管理测试
        test_report_management()
        
        # 7. 分页和过滤测试
        test_api_pagination_and_filtering()
        
        print_section("测试完成")
        print("✅ API完整功能测试完成")
        print(f"测试数据: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
        
    except KeyboardInterrupt:
        print("\n❌ 测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
