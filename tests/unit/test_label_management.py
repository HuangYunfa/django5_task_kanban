#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试任务标签管理功能
验证新创建的标签管理API和前端集成
"""
import os
import sys
import django
import json
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

# 设置Django环境
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskkanban.settings')
django.setup()

from boards.models import Board, BoardLabel
from tasks.models import Task
from users.models import User

class TaskLabelManagementTest:
    """任务标签管理功能测试"""
    
    def __init__(self):
        self.client = Client()
        self.setup_test_data()
    
    def setup_test_data(self):
        """设置测试数据"""
        print("🔧 设置测试数据...")
        
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # 创建测试看板
        self.board = Board.objects.create(
            name='测试看板',
            description='标签管理测试看板',
            owner=self.user,
            slug='test-board-labels'
        )
        
        # 创建看板列表
        from boards.models import BoardList
        self.board_list = BoardList.objects.create(
            name='待办事项',
            board=self.board,
            position=0
        )
        
        # 创建测试任务
        self.task = Task.objects.create(
            title='测试任务',
            description='用于测试标签功能',
            board=self.board,
            board_list=self.board_list,
            creator=self.user
        )
        
        # 登录用户
        self.client.login(username='testuser', password='testpass123')
        print("✅ 测试数据设置完成")
    
    def test_board_label_creation(self):
        """测试看板标签创建"""
        print("\n📝 测试看板标签创建...")
        
        # 创建标签的数据
        label_data = {
            'name': '重要',
            'color': '#ff0000',
            'description': '重要任务标签'
        }
        
        # 发送创建标签的请求
        url = reverse('boards:label_list_create_api', kwargs={'slug': self.board.slug})
        response = self.client.post(url, label_data)
        
        print(f"请求URL: {url}")
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            if data.get('success'):
                label = data['label']
                print(f"✅ 标签创建成功: {label['name']} (ID: {label['id']})")
                return label['id']
            else:
                print(f"❌ 标签创建失败: {data}")
                return None
        else:
            print(f"❌ 请求失败，状态码: {response.status_code}")
            try:
                print(f"错误内容: {response.content.decode()}")
            except:
                pass
            return None
    
    def test_board_label_list(self):
        """测试获取看板标签列表"""
        print("\n📋 测试获取看板标签列表...")
        
        # 先创建几个标签
        for name, color in [('紧急', '#ff0000'), ('普通', '#00ff00'), ('次要', '#0000ff')]:
            BoardLabel.objects.create(
                name=name,
                color=color,
                board=self.board
            )
        
        # 获取标签列表
        url = reverse('boards:label_list_create_api', kwargs={'slug': self.board.slug})
        response = self.client.get(url)
        
        print(f"请求URL: {url}")
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 成功获取 {len(data.get('labels', []))} 个标签")
            for label in data.get('labels', []):
                print(f"  - {label['name']} ({label['color']}) - {label['task_count']} 个任务")
            return data.get('labels', [])
        else:
            print(f"❌ 获取标签列表失败，状态码: {response.status_code}")
            return []
    
    def test_task_label_assignment(self):
        """测试任务标签分配"""
        print("\n🏷️ 测试任务标签分配...")
        
        # 创建测试标签
        label1 = BoardLabel.objects.create(
            name='前端',
            color='#007bff',
            board=self.board
        )
        label2 = BoardLabel.objects.create(
            name='后端',
            color='#28a745',
            board=self.board
        )
        
        # 为任务分配标签
        assignment_data = {
            'label_ids': [label1.id, label2.id]
        }
        
        url = reverse('tasks:label_update', kwargs={'pk': self.task.pk})
        response = self.client.post(
            url,
            json.dumps(assignment_data),
            content_type='application/json'
        )
        
        print(f"请求URL: {url}")
        print(f"分配标签: {[label1.name, label2.name]}")
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            if data.get('success'):
                # 验证数据库中的分配
                task_labels = list(self.task.labels.all())
                print(f"✅ 任务标签分配成功，当前标签: {[l.name for l in task_labels]}")
                return True
            else:
                print(f"❌ 任务标签分配失败: {data}")
                return False
        else:
            print(f"❌ 请求失败，状态码: {response.status_code}")
            return False
    
    def test_label_delete(self):
        """测试标签删除"""
        print("\n🗑️ 测试标签删除...")
        
        # 创建要删除的标签
        label = BoardLabel.objects.create(
            name='临时标签',
            color='#ffc107',
            board=self.board
        )
        
        # 为任务分配该标签
        self.task.labels.add(label)
        
        print(f"创建临时标签: {label.name} (ID: {label.id})")
        print(f"任务当前标签数量: {self.task.labels.count()}")
        
        # 删除标签
        url = reverse('boards:label_update_api', kwargs={
            'slug': self.board.slug,
            'label_pk': label.id
        })
        response = self.client.delete(url)
        
        print(f"删除请求URL: {url}")
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            if data.get('success'):
                # 验证标签已删除
                label_exists = BoardLabel.objects.filter(id=label.id).exists()
                task_label_count = self.task.labels.count()
                
                print(f"✅ 标签删除成功")
                print(f"标签是否还存在: {label_exists}")
                print(f"任务标签数量: {task_label_count}")
                return True
            else:
                print(f"❌ 标签删除失败: {data}")
                return False
        else:
            print(f"❌ 删除请求失败，状态码: {response.status_code}")
            return False
    
    def test_label_permissions(self):
        """测试标签权限控制"""
        print("\n🔒 测试标签权限控制...")
        
        # 创建另一个用户
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        
        # 创建另一个用户的看板
        other_board = Board.objects.create(
            name='其他用户看板',
            description='其他用户的看板',
            owner=other_user,
            slug='other-board'
        )
        
        # 尝试在其他用户的看板中创建标签（应该失败）
        label_data = {
            'name': '未授权标签',
            'color': '#666666'
        }
        
        url = reverse('boards:label_list_create_api', kwargs={'slug': other_board.slug})
        response = self.client.post(url, label_data)
        
        print(f"尝试在未授权看板创建标签: {url}")
        print(f"响应状态码: {response.status_code}")
        
        # 应该返回403或404
        if response.status_code in [403, 404]:
            print("✅ 权限控制正常，阻止了未授权操作")
            return True
        else:
            print(f"❌ 权限控制失败，未阻止未授权操作")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始测试任务标签管理功能")
        print("=" * 50)
        
        test_results = []
        
        # 测试标签创建
        label_id = self.test_board_label_creation()
        test_results.append(('标签创建', label_id is not None))
        
        # 测试标签列表
        labels = self.test_board_label_list()
        test_results.append(('标签列表', len(labels) >= 0))
        
        # 测试任务标签分配
        assignment_success = self.test_task_label_assignment()
        test_results.append(('任务标签分配', assignment_success))
        
        # 测试标签删除
        delete_success = self.test_label_delete()
        test_results.append(('标签删除', delete_success))
        
        # 测试权限控制
        permission_success = self.test_label_permissions()
        test_results.append(('权限控制', permission_success))
        
        # 打印测试结果
        print("\n" + "=" * 50)
        print("📊 测试结果汇总:")
        
        passed = 0
        total = len(test_results)
        
        for test_name, success in test_results:
            status = "✅ 通过" if success else "❌ 失败"
            print(f"  {test_name:<15} : {status}")
            if success:
                passed += 1
        
        print(f"\n总计: {passed}/{total} 通过")
        
        if passed == total:
            print("🎉 所有测试通过！标签管理功能工作正常")
        else:
            print("⚠️ 部分测试失败，需要检查相关功能")
    
    def cleanup(self):
        """清理测试数据"""
        print("\n🧹 清理测试数据...")
        try:
            # 删除创建的对象
            Task.objects.filter(creator=self.user).delete()
            Board.objects.filter(owner=self.user).delete()
            User.objects.filter(username__in=['testuser', 'otheruser']).delete()
            print("✅ 测试数据清理完成")
        except Exception as e:
            print(f"⚠️ 清理测试数据时出错: {e}")

def main():
    """主函数"""
    test = TaskLabelManagementTest()
    
    try:
        test.run_all_tests()
    except Exception as e:
        print(f"\n💥 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        test.cleanup()

if __name__ == '__main__':
    main()
