"""
测试报表分析模块的功能
"""
import json
from datetime import datetime, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from teams.models import Team, TeamMembership
from boards.models import Board, BoardList, BoardMember
from tasks.models import Task
from tasks.workflow_models import WorkflowStatus
from reports.models import Report
from reports.chart_services import ChartDataService

User = get_user_model()


class ReportViewsTestCase(TestCase):
    """报表视图测试用例"""
    
    def setUp(self):
        """测试前初始化"""
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # 创建测试团队
        self.team = Team.objects.create(
            name='测试团队',
            description='用于测试的团队',
            created_by=self.user
        )
        
        # 创建团队成员关系
        TeamMembership.objects.create(
            team=self.team,
            user=self.user,
            role='admin',
            status='active'
        )
        
        # 创建看板
        self.board = Board.objects.create(name='测试看板', description='用于测试的看板', owner=self.user)
        
        # 创建看板列表
        self.board_list = BoardList.objects.create(
            name='待办事项',
            board=self.board,
            position=0
        )
        
        # 创建测试任务
        for i in range(10):
            status = 'todo'
            if i < 3:
                status = 'done'
            elif i < 7:
                status = 'in_progress'
            
            task = Task.objects.create(
                title=f'测试任务 {i+1}',
                description=f'用于测试的任务 {i+1}',
                board=self.board,
                board_list=self.board_list,
                status=status,
                priority='medium' if i % 2 == 0 else 'high',
                creator=self.user
            )
            task.assignees.add(self.user)
            
            # 调整创建时间以便测试日期范围筛选
            if i < 5:
                created_date = datetime.now() - timedelta(days=i*2)
            else:
                created_date = datetime.now() - timedelta(days=40 + i)
            
            # 使用update跳过auto_now_add的限制
            Task.objects.filter(pk=task.pk).update(
                created_at=created_date,
                updated_at=created_date
            )
        
        # 创建测试报表
        self.report = Report.objects.create(
            name='测试报表',
            description='用于测试的报表',
            report_type='task_completion',
            created_by=self.user
        )
        
        # 客户端登录
        self.client = Client()
        self.client.login(username='testuser', password='testpassword')
    
    def test_report_index_view(self):
        """测试报表首页视图"""
        url = reverse('reports:index')
        response = self.client.get(url)
        
        # 验证状态码
        self.assertEqual(response.status_code, 200)
        
        # 验证上下文数据
        self.assertIn('filter_form', response.context)
        self.assertIn('chart_data', response.context)
        self.assertIn('task_completion_trend', response.context['chart_data'])
        self.assertIn('status_distribution', response.context['chart_data'])
        self.assertIn('user_workload', response.context['chart_data'])
        
        # 验证页面内容
        self.assertContains(response, '数据报表')
        self.assertContains(response, '任务完成趋势')
        self.assertContains(response, '任务状态分布')
        self.assertContains(response, '用户工作负载')
    
    def test_report_filter(self):
        """测试报表筛选功能"""
        # 测试时间范围筛选
        url = reverse('reports:index')
        response = self.client.get(url, {'time_range': '7days'})
        
        # 验证筛选结果
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['filter_form'].cleaned_data['time_range'], '7days')
        
        # 测试看板筛选
        response = self.client.get(url, {'board': self.board.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['filter_form'].cleaned_data['board'], self.board)
    
    def test_report_export(self):
        """测试报表导出功能"""
        # 测试Excel导出
        url = reverse('reports:export')
        response = self.client.get(url, {'export_format': 'excel'})
          # 验证响应
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        
        # 检查Content-Disposition头部，兼容不同Django版本的编码方式
        content_disposition = response['Content-Disposition']
        self.assertTrue(
            'attachment;' in content_disposition.lower() or
            'attachment; ' in content_disposition.lower(),
            f"Content-Disposition头部应该包含'attachment'，实际值：{content_disposition}"
        )
        
        # 测试CSV导出
        response = self.client.get(url, {'export_format': 'csv'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv; charset=utf-8')
        
        # 同样检查CSV导出的Content-Disposition
        content_disposition = response['Content-Disposition']
        self.assertTrue(
            'attachment;' in content_disposition.lower() or
            'attachment; ' in content_disposition.lower(),
            f"CSV导出的Content-Disposition头部应该包含'attachment'，实际值：{content_disposition}"
        )
        
        # 测试JSON导出
        response = self.client.get(url, {'export_format': 'json'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        # 验证导出的JSON内容
        data = json.loads(response.content)
        self.assertIn('summary', data)
        self.assertIn('task_stats', data)
    
    def test_chart_data_service(self):
        """测试图表数据服务"""
        # 测试折线图数据格式化
        line_data = [
            {'date': '2023-01-01', 'value': 10},
            {'date': '2023-01-02', 'value': 15},
            {'date': '2023-01-03', 'value': 8}
        ]
        
        formatted = ChartDataService.format_for_chartjs(line_data, 'line')
        self.assertEqual(len(formatted['labels']), 3)
        self.assertEqual(len(formatted['datasets']), 1)
        self.assertEqual(len(formatted['datasets'][0]['data']), 3)
        
        # 测试饼图数据格式化
        pie_data = [
            {'label': '已完成', 'value': 10},
            {'label': '进行中', 'value': 15},
            {'label': '待办', 'value': 8}
        ]
        
        formatted = ChartDataService.format_for_chartjs(pie_data, 'doughnut')
        self.assertEqual(len(formatted['labels']), 3)
        self.assertEqual(len(formatted['datasets']), 1)
        self.assertEqual(len(formatted['datasets'][0]['data']), 3)
