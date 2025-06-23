#!/usr/bin/env python3
"""
简化API测试脚本
专门测试新的API端点
"""

import requests
import json
from datetime import datetime

BASE_URL = 'http://127.0.0.1:8000'

def test_complete_api_workflow():
    """完整API工作流测试"""
    print("🔍 完整API工作流测试")
    
    # 1. 创建用户
    user_data = {
        'username': f'apitest_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
        'email': f'apitest_{datetime.now().strftime("%Y%m%d_%H%M%S")}@example.com',
        'password': 'apitest123',
        'password_confirm': 'apitest123',
        'first_name': 'API',
        'last_name': 'Test'
    }
    
    print("\n1️⃣ 创建用户...")
    response = requests.post(f"{BASE_URL}/api/v1/users/", json=user_data)
    if response.status_code == 201:
        user_info = response.json()
        print(f"✅ 用户创建成功: {user_info['username']}")
        user_id = user_info.get('id') or user_info.get('username')  # 适应不同的响应格式
    else:
        print(f"❌ 用户创建失败: {response.status_code} - {response.text}")
        return
    
    # 2. 用户登录
    print("\n2️⃣ 用户登录...")
    login_data = {
        'email': user_data['email'],
        'password': user_data['password']
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login/", json=login_data)
    if response.status_code == 200:
        tokens = response.json()
        access_token = tokens['access']
        print("✅ 登录成功，获取到JWT令牌")
    else:
        print(f"❌ 登录失败: {response.status_code} - {response.text}")
        return
    
    # 设置认证头
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # 3. 检查API端点列表
    print("\n3️⃣ 检查API端点...")
    response = requests.get(f"{BASE_URL}/api/v1/", headers=headers)
    if response.status_code == 200:
        endpoints = response.json()
        print(f"✅ API端点获取成功，可用端点: {list(endpoints.keys())}")
    else:
        print(f"❌ API端点获取失败: {response.status_code}")
    
    # 4. 获取当前用户信息
    print("\n4️⃣ 获取当前用户信息...")
    response = requests.get(f"{BASE_URL}/api/v1/users/me/", headers=headers)
    if response.status_code == 200:
        user_info = response.json()
        print(f"✅ 用户信息获取成功: {user_info['username']}")
    else:
        print(f"❌ 用户信息获取失败: {response.status_code}")
    
    # 5. 创建看板
    print("\n5️⃣ 创建看板...")
    board_data = {
        'title': 'API测试看板',
        'description': '通过API创建的测试看板',
        'is_private': False
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/boards/", json=board_data, headers=headers)
    if response.status_code == 201:
        board_info = response.json()
        board_id = board_info['id']
        print(f"✅ 看板创建成功: {board_info['title']} (ID: {board_id})")
    else:
        print(f"❌ 看板创建失败: {response.status_code} - {response.text}")
        board_id = None
    
    # 6. 获取看板列表
    print("\n6️⃣ 获取看板列表...")
    response = requests.get(f"{BASE_URL}/api/v1/boards/", headers=headers)
    if response.status_code == 200:
        boards_data = response.json()
        boards_count = len(boards_data.get('results', boards_data))
        print(f"✅ 看板列表获取成功，共 {boards_count} 个看板")
    else:
        print(f"❌ 看板列表获取失败: {response.status_code}")
    
    # 7. 创建团队
    print("\n7️⃣ 创建团队...")
    team_data = {
        'name': 'API测试团队',
        'description': '通过API创建的测试团队'
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/teams/", json=team_data, headers=headers)
    if response.status_code == 201:
        team_info = response.json()
        team_id = team_info['id']
        print(f"✅ 团队创建成功: {team_info['name']} (ID: {team_id})")
    else:
        print(f"❌ 团队创建失败: {response.status_code} - {response.text}")
        team_id = None
    
    # 8. 获取团队列表
    print("\n8️⃣ 获取团队列表...")
    response = requests.get(f"{BASE_URL}/api/v1/teams/", headers=headers)
    if response.status_code == 200:
        teams_data = response.json()
        teams_count = len(teams_data.get('results', teams_data))
        print(f"✅ 团队列表获取成功，共 {teams_count} 个团队")
    else:
        print(f"❌ 团队列表获取失败: {response.status_code}")
    
    # 9. 创建报表
    print("\n9️⃣ 创建报表...")
    report_data = {
        'name': 'API测试报表',
        'description': '通过API创建的测试报表',
        'report_type': 'task_summary',
        'filters': {
            'date_range': 30
        }
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/reports/", json=report_data, headers=headers)
    if response.status_code == 201:
        report_info = response.json()
        report_id = report_info['id']
        print(f"✅ 报表创建成功: {report_info['name']} (ID: {report_id})")
        
        # 10. 获取报表数据
        print("\n🔟 获取报表数据...")
        response = requests.get(f"{BASE_URL}/api/v1/reports/{report_id}/data/", headers=headers)
        if response.status_code == 200:
            report_data = response.json()
            print(f"✅ 报表数据获取成功: {json.dumps(report_data, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 报表数据获取失败: {response.status_code}")
    else:
        print(f"❌ 报表创建失败: {response.status_code} - {response.text}")
    
    # 11. 获取任务列表
    print("\n1️⃣1️⃣ 获取任务列表...")
    response = requests.get(f"{BASE_URL}/api/v1/tasks/", headers=headers)
    if response.status_code == 200:
        tasks_data = response.json()
        tasks_count = len(tasks_data.get('results', tasks_data))
        print(f"✅ 任务列表获取成功，共 {tasks_count} 个任务")
    else:
        print(f"❌ 任务列表获取失败: {response.status_code}")
    
    # 12. 测试团队绩效端点
    if team_id:
        print("\n1️⃣2️⃣ 测试团队绩效...")
        response = requests.get(f"{BASE_URL}/api/v1/teams/{team_id}/performance/", headers=headers)
        if response.status_code == 200:
            performance_data = response.json()
            print(f"✅ 团队绩效获取成功: 团队 '{performance_data['team_name']}' 有 {performance_data['member_count']} 个成员")
        else:
            print(f"❌ 团队绩效获取失败: {response.status_code}")
    
    print("\n🎉 API工作流测试完成！")

def main():
    print("🚀 API端点测试开始")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        test_complete_api_workflow()
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
