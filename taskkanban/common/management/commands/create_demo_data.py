from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random

from boards.models import Board, BoardList, BoardLabel
from tasks.models import Task, TaskComment
from teams.models import Team, TeamMembership
from notifications.models import EmailTemplate, UserNotificationPreference

User = get_user_model()

class Command(BaseCommand):
    help = '创建完整的演示数据，展示所有模块功能'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='重置现有数据 (警告: 将删除所有演示数据)',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.reset_data()
        
        self.stdout.write(self.style.SUCCESS('🚀 开始创建演示数据...'))
        
        # 1. 创建用户
        users = self.create_users()
        
        # 2. 创建团队
        teams = self.create_teams(users)
        
        # 3. 创建看板
        boards = self.create_boards(users, teams)
        
        # 4. 创建任务标签
        labels = self.create_task_labels(boards)
        
        # 5. 创建任务
        tasks = self.create_tasks(boards, users, labels)
        
        # 6. 创建任务评论
        self.create_task_comments(tasks, users)
        
        # 7. 创建邮件模板
        self.create_email_templates()
        
        # 8. 设置用户通知偏好
        self.setup_user_preferences(users)
        
        self.stdout.write(self.style.SUCCESS('✅ 演示数据创建完成！'))
        self.show_summary()

    def reset_data(self):
        """重置演示数据"""
        self.stdout.write(self.style.WARNING('🗑️  重置现有数据...'))
        
        # 删除顺序很重要，避免外键约束问题
        TaskComment.objects.all().delete()
        Task.objects.all().delete()
        BoardLabel.objects.all().delete()
        BoardList.objects.all().delete()
        Board.objects.all().delete()
        TeamMembership.objects.all().delete()
        Team.objects.all().delete()
        
        # 保留超级用户，删除其他演示用户
        User.objects.exclude(is_superuser=True).delete()
        
        self.stdout.write(self.style.SUCCESS('✅ 数据重置完成'))

    def create_users(self):
        """创建演示用户"""
        self.stdout.write('👥 创建用户...')
        
        users_data = [
            {
                'username': 'project_manager',
                'email': 'pm@example.com',
                'first_name': '项目',
                'last_name': '经理',
                'is_staff': True,
            },
            {
                'username': 'developer1',
                'email': 'dev1@example.com',
                'first_name': '张',
                'last_name': '三',
            },
            {
                'username': 'developer2',
                'email': 'dev2@example.com',
                'first_name': '李',
                'last_name': '四',
            },
            {
                'username': 'designer',
                'email': 'designer@example.com',
                'first_name': '王',
                'last_name': '五',
            },
            {
                'username': 'tester',
                'email': 'tester@example.com',
                'first_name': '赵',
                'last_name': '六',
            },
        ]
        
        users = []
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    **user_data,
                    'password': 'demo123456',  # 会被下面的set_password覆盖
                }
            )
            if created:
                user.set_password('demo123456')
                user.save()
                self.stdout.write(f'  ✅ 创建用户: {user.username}')
            else:
                self.stdout.write(f'  ℹ️  用户已存在: {user.username}')
            users.append(user)
        
        return users

    def create_teams(self, users):
        """创建团队"""
        self.stdout.write('🏢 创建团队...')
        
        teams_data = [
            {
                'name': '前端开发团队',
                'description': '负责前端界面开发和用户体验优化',
                'creator': users[0],  # project_manager
                'members': [users[0], users[1], users[3]],  # pm, dev1, designer
            },
            {
                'name': '后端开发团队',
                'description': '负责后端API开发和数据库设计',
                'creator': users[0],
                'members': [users[0], users[1], users[2]],  # pm, dev1, dev2
            },
            {
                'name': '测试团队',
                'description': '负责产品质量保证和测试',
                'creator': users[0],
                'members': [users[0], users[4]],  # pm, tester
            },
        ]
        
        teams = []
        for team_data in teams_data:
            team, created = Team.objects.get_or_create(
                name=team_data['name'],                defaults={
                    'description': team_data['description'],
                    'created_by': team_data['creator'],
                }
            )
            
            if created:
                # 添加团队成员
                for user in team_data['members']:
                    role = 'leader' if user == team_data['creator'] else 'member'
                    TeamMembership.objects.create(
                        team=team,
                        user=user,
                        role=role,
                    )
                self.stdout.write(f'  ✅ 创建团队: {team.name}')
            else:
                self.stdout.write(f'  ℹ️  团队已存在: {team.name}')
            
            teams.append(team)
        
        return teams

    def create_boards(self, users, teams):
        """创建看板"""
        self.stdout.write('📋 创建看板...')
        
        boards_data = [
            {
                'name': '企业看板系统开发',
                'description': '开发一个功能完整的企业级任务看板系统',
                'creator': users[0],
                'team': teams[0],
                'lists': ['需求分析', '开发中', '测试中', '已完成'],
            },
            {
                'name': '移动端应用开发',
                'description': '开发配套的移动端应用',
                'creator': users[0],
                'team': teams[1],
                'lists': ['产品设计', '开发中', '联调测试', '发布准备'],
            },
            {
                'name': '系统运维优化',
                'description': '优化系统性能和运维流程',
                'creator': users[0],
                'team': teams[2],
                'lists': ['待处理', '进行中', '验证中', '已完成'],
            },
        ]
        
        boards = []
        for board_data in boards_data:
            board, created = Board.objects.get_or_create(
                name=board_data['name'],                defaults={
                    'description': board_data['description'],
                    'owner': board_data['creator'],
                    'team': board_data['team'],
                }
            )
            
            if created:
                # 创建看板列表
                for i, list_name in enumerate(board_data['lists']):
                    BoardList.objects.create(
                        board=board,
                        name=list_name,
                        position=i,
                    )
                self.stdout.write(f'  ✅ 创建看板: {board.name}')
            else:
                self.stdout.write(f'  ℹ️  看板已存在: {board.name}')
            
            boards.append(board)
        
        return boards

    def create_task_labels(self, boards):
        """创建任务标签"""
        self.stdout.write('🏷️  创建任务标签...')
        
        labels_data = [
            {'name': '高优先级', 'color': '#dc3545'},
            {'name': '中优先级', 'color': '#ffc107'},
            {'name': '低优先级', 'color': '#28a745'},
            {'name': 'Bug修复', 'color': '#e74c3c'},
            {'name': '新功能', 'color': '#3498db'},
            {'name': '优化', 'color': '#9b59b6'},
            {'name': '文档', 'color': '#f39c12'},
            {'name': '测试', 'color': '#1abc9c'},
        ]
        
        all_labels = []
        # 为每个看板创建标签
        for board in boards:
            board_labels = []
            for label_data in labels_data:
                label, created = BoardLabel.objects.get_or_create(
                    board=board,
                    name=label_data['name'],
                    defaults={'color': label_data['color']}
                )
                
                if created:
                    self.stdout.write(f'  ✅ 为看板 {board.name} 创建标签: {label.name}')
                
                board_labels.append(label)
            all_labels.extend(board_labels)
        
        return all_labels

    def create_tasks(self, boards, users, labels):
        """创建任务"""
        self.stdout.write('📝 创建任务...')
        
        tasks = []
        
        # 为每个看板创建任务
        for board in boards:
            board_lists = list(board.lists.all())
            
            if board.name == '企业看板系统开发':
                tasks_data = [
                    {
                        'title': '用户需求调研',
                        'description': '调研企业用户对任务管理系统的具体需求',
                        'board_list': board_lists[0],  # 需求分析
                        'priority': 'high',
                        'labels': ['新功能', '高优先级'],
                    },
                    {
                        'title': '数据库设计',
                        'description': '设计用户、看板、任务等核心数据模型',
                        'board_list': board_lists[1],  # 开发中
                        'priority': 'high',
                        'labels': ['新功能', '高优先级'],
                    },
                    {
                        'title': '用户认证系统',
                        'description': '实现用户注册、登录、权限管理功能',
                        'board_list': board_lists[1],  # 开发中
                        'priority': 'medium',
                        'labels': ['新功能', '中优先级'],
                    },
                    {
                        'title': '看板拖拽功能',
                        'description': '实现任务在看板列表间的拖拽移动',
                        'board_list': board_lists[2],  # 测试中
                        'priority': 'medium',
                        'labels': ['新功能', '中优先级'],
                    },
                    {
                        'title': '邮件通知系统',
                        'description': '实现任务分配、状态变更等邮件通知',
                        'board_list': board_lists[1],  # 开发中
                        'priority': 'medium',
                        'labels': ['新功能', '中优先级'],
                    },
                    {
                        'title': '项目文档编写',
                        'description': '编写项目使用手册和开发文档',
                        'board_list': board_lists[3],  # 已完成
                        'priority': 'low',
                        'labels': ['文档', '低优先级'],
                    },
                ]
            elif board.name == '移动端应用开发':
                tasks_data = [
                    {
                        'title': 'UI设计稿',
                        'description': '设计移动端应用的界面原型',
                        'board_list': board_lists[0],  # 产品设计
                        'priority': 'high',
                        'labels': ['新功能', '高优先级'],
                    },
                    {
                        'title': 'React Native框架搭建',
                        'description': '搭建移动端开发框架和基础配置',
                        'board_list': board_lists[1],  # 开发中
                        'priority': 'high',
                        'labels': ['新功能', '高优先级'],
                    },
                    {
                        'title': 'API对接',
                        'description': '移动端与后端API的对接和联调',
                        'board_list': board_lists[2],  # 联调测试
                        'priority': 'medium',
                        'labels': ['新功能', '中优先级'],
                    },
                ]
            else:  # 系统运维优化
                tasks_data = [
                    {
                        'title': '数据库性能优化',
                        'description': '优化数据库查询性能，添加必要索引',
                        'board_list': board_lists[1],  # 进行中
                        'priority': 'high',
                        'labels': ['优化', '高优先级'],
                    },
                    {
                        'title': 'Redis缓存配置',
                        'description': '配置Redis缓存提升系统响应速度',
                        'board_list': board_lists[0],  # 待处理
                        'priority': 'medium',
                        'labels': ['优化', '中优先级'],
                    },
                    {
                        'title': '日志监控系统',
                        'description': '建立完善的日志收集和监控系统',
                        'board_list': board_lists[3],  # 已完成
                        'priority': 'low',
                        'labels': ['优化', '低优先级'],
                    },
                ]
            
            # 创建任务
            for i, task_data in enumerate(tasks_data):
                task = Task.objects.create(
                    title=task_data['title'],
                    description=task_data['description'],
                    board=board,
                    board_list=task_data['board_list'],
                    creator=users[0],  # 都由项目经理创建
                    priority=task_data['priority'],
                    position=i,
                    due_date=timezone.now() + timedelta(days=random.randint(7, 30)),
                )
                
                # 随机分配任务给团队成员
                assignee = random.choice(users[1:])  # 不包括项目经理
                task.assignees.add(assignee)
                
                # 添加标签
                for label_name in task_data['labels']:
                    label = next((l for l in labels if l.name == label_name), None)
                    if label:
                        task.labels.add(label)
                
                tasks.append(task)
        
        self.stdout.write(f'  ✅ 创建了 {len(tasks)} 个任务')
        return tasks

    def create_task_comments(self, tasks, users):
        """创建任务评论"""
        self.stdout.write('💬 创建任务评论...')
        
        comments_data = [
            '这个功能的优先级很高，需要尽快完成。',
            '我觉得这里可能需要考虑一下用户体验。',
            '代码审查通过，可以合并了。',
            '测试发现了一个小问题，已经修复。',
            '文档需要补充一些使用示例。',
            '这个模块的性能需要优化一下。',
            'UI设计很棒，用户会喜欢的。',
            '接口文档已经更新，请查看。',
        ]
        
        comment_count = 0
        for task in tasks[:10]:  # 只为前10个任务添加评论
            # 每个任务随机添加1-3个评论
            num_comments = random.randint(1, 3)
            for i in range(num_comments):
                TaskComment.objects.create(
                    task=task,
                    user=random.choice(users),
                    content=random.choice(comments_data),
                )
                comment_count += 1
        
        self.stdout.write(f'  ✅ 创建了 {comment_count} 个评论')

    def create_email_templates(self):
        """创建邮件模板"""
        self.stdout.write('📧 创建邮件模板...')
        
        # 这个在test_notifications命令中已经实现了
        from notifications.management.commands.test_notifications import Command as NotificationCommand
        cmd = NotificationCommand()
        cmd.create_basic_templates()
        
        self.stdout.write('  ✅ 邮件模板创建完成')

    def setup_user_preferences(self, users):
        """设置用户通知偏好"""
        self.stdout.write('⚙️  设置用户通知偏好...')
        
        from notifications.services import EmailService
        
        for user in users:
            preference = EmailService.get_user_preference(user)
            # 设置为已验证，这样可以接收邮件
            preference.email_verified = True
            preference.save()
        
        self.stdout.write(f'  ✅ 设置了 {len(users)} 个用户的通知偏好')

    def show_summary(self):
        """显示创建摘要"""
        self.stdout.write('\n📊 演示数据摘要:')
        self.stdout.write(f'  👥 用户: {User.objects.count()} 个')
        self.stdout.write(f'  🏢 团队: {Team.objects.count()} 个')
        self.stdout.write(f'  📋 看板: {Board.objects.count()} 个')
        self.stdout.write(f'  📝 任务: {Task.objects.count()} 个')
        self.stdout.write(f'  🏷️  标签: {BoardLabel.objects.count()} 个')
        self.stdout.write(f'  💬 评论: {TaskComment.objects.count()} 个')
        self.stdout.write(f'  📧 邮件模板: {EmailTemplate.objects.count()} 个')
        
        self.stdout.write('\n🔐 测试账号 (密码: demo123456):')
        for user in User.objects.exclude(is_superuser=True):
            role = '项目经理' if user.is_staff else '团队成员'
            self.stdout.write(f'  • {user.username} ({role}) - {user.email}')
        
        self.stdout.write('\n🎯 功能测试建议:')
        self.stdout.write('  1. 使用不同账号登录体验权限差异')
        self.stdout.write('  2. 在看板中拖拽任务测试状态流转')
        self.stdout.write('  3. 查看报表分析了解数据可视化')
        self.stdout.write('  4. 测试团队邀请和成员管理')
        self.stdout.write('  5. 配置邮件通知偏好和测试邮件发送')
        self.stdout.write('  6. 使用API接口进行数据操作')
