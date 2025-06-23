#!/usr/bin/env python3
"""
批量UX修复脚本
自动修复所有模板页面的UX问题，确保统一的视觉层次和用户体验
"""

import os
import re
import glob
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent

# 模板目录
TEMPLATES_DIR = PROJECT_ROOT / "taskkanban" / "templates"

class UXFixer:
    def __init__(self):
        self.fixes_applied = []
        
    def add_page_header(self, content, page_info):
        """添加页面头部"""
        page_header = f'''
<!-- 页面头部 -->
<div class="page-header">
    <div class="container">
        <div class="row align-items-center">
            <div class="col-md-8">
                <h1 class="mb-0">
                    <i class="fas fa-{page_info['icon']} me-3"></i>
                    {page_info['title']}
                </h1>
                <p class="lead mb-0">{page_info['description']}</p>
            </div>
            <div class="col-md-4 text-md-end">
                {page_info.get('action_button', '')}
            </div>
        </div>
    </div>
</div>

'''
        
        # 在content开始后插入页面头部
        content_match = re.search(r'{% block content %}', content)
        if content_match:
            insert_pos = content_match.end()
            content = content[:insert_pos] + page_header + content[insert_pos:]
        
        return content
    
    def fix_form_styling(self, content):
        """修复表单样式"""
        # 添加Bootstrap form-control类
        content = re.sub(
            r'<input([^>]*?)(?:class="([^"]*?)")?([^>]*?)>',
            lambda m: f'<input{m.group(1)}class="{m.group(2) + " " if m.group(2) else ""}form-control"{m.group(3)}>',
            content
        )
        
        # 添加Bootstrap select样式
        content = re.sub(
            r'<select([^>]*?)(?:class="([^"]*?)")?([^>]*?)>',
            lambda m: f'<select{m.group(1)}class="{m.group(2) + " " if m.group(2) else ""}form-select"{m.group(3)}>',
            content
        )
        
        # 添加Bootstrap textarea样式
        content = re.sub(
            r'<textarea([^>]*?)(?:class="([^"]*?)")?([^>]*?)>',
            lambda m: f'<textarea{m.group(1)}class="{m.group(2) + " " if m.group(2) else ""}form-control"{m.group(3)}>',
            content
        )
        
        return content
    
    def add_stats_cards(self, content, stats_info):
        """添加统计卡片"""
        if not stats_info:
            return content
        
        stats_html = '''
<!-- 统计卡片 -->
<div class="row g-4 mb-5">
'''
        
        for stat in stats_info:
            stats_html += f'''
    <div class="col-md-3 col-6">
        <div class="card stats-card h-100">
            <div class="card-body text-center">
                <div class="stats-number text-{stat['color']}">{stat['value']}</div>
                <div class="stats-label">{stat['label']}</div>
                <div class="mt-3">
                    <i class="fas fa-{stat['icon']} text-{stat['color']} fa-2x"></i>
                </div>
            </div>
        </div>
    </div>
'''
        
        stats_html += '''
</div>
'''
        
        # 在页面头部后插入统计卡片
        header_match = re.search(r'</div>\s*</div>\s*</div>\s*<!-- 页面头部 -->', content)
        if header_match:
            insert_pos = header_match.end()
            content = content[:insert_pos] + stats_html + content[insert_pos:]
        
        return content
    
    def get_page_info(self, file_path):
        """根据文件路径获取页面信息"""
        path_str = str(file_path).lower()
        
        page_configs = {
            'create': {
                'icon': 'plus',
                'title': '创建',
                'description': '创建新的项目内容'
            },
            'edit': {
                'icon': 'edit',
                'title': '编辑',
                'description': '修改现有内容'
            },
            'list': {
                'icon': 'list',
                'title': '列表',
                'description': '查看所有项目'
            },
            'detail': {
                'icon': 'eye',
                'title': '详情',
                'description': '查看详细信息'
            },
            'tasks': {
                'icon': 'tasks',
                'title': '任务管理',
                'description': '管理和跟踪您的所有任务',
                'action_button': '<a href="#" class="btn btn-light btn-lg"><i class="fas fa-plus me-2"></i>新建任务</a>'
            },
            'teams': {
                'icon': 'users',
                'title': '团队协作',
                'description': '管理团队成员和项目',
                'action_button': '<a href="#" class="btn btn-light btn-lg"><i class="fas fa-plus me-2"></i>创建团队</a>'
            },
            'boards': {
                'icon': 'columns',
                'title': '看板管理',
                'description': '可视化任务看板',
                'action_button': '<a href="#" class="btn btn-light btn-lg"><i class="fas fa-plus me-2"></i>新建看板</a>'
            },
            'reports': {
                'icon': 'chart-bar',
                'title': '报表分析',
                'description': '数据统计与分析',
                'action_button': '<a href="#" class="btn btn-light btn-lg"><i class="fas fa-plus me-2"></i>生成报表</a>'
            },
            'users': {
                'icon': 'user',
                'title': '用户管理',
                'description': '个人设置与信息管理'
            },
            'notifications': {
                'icon': 'bell',
                'title': '通知中心',
                'description': '消息提醒与通知设置'
            }
        }
        
        # 根据路径匹配配置
        for key, config in page_configs.items():
            if key in path_str:
                return config
        
        # 默认配置
        return {
            'icon': 'home',
            'title': '页面',
            'description': '页面内容'
        }
    
    def get_stats_info(self, file_path):
        """根据文件路径获取统计信息配置"""
        path_str = str(file_path).lower()
        
        if 'tasks' in path_str and 'list' in path_str:
            return [
                {'value': '{{ task_stats.total|default:0 }}', 'label': '总任务', 'icon': 'tasks', 'color': 'primary'},
                {'value': '{{ task_stats.todo|default:0 }}', 'label': '待办', 'icon': 'clock', 'color': 'warning'},
                {'value': '{{ task_stats.in_progress|default:0 }}', 'label': '进行中', 'icon': 'play', 'color': 'info'},
                {'value': '{{ task_stats.done|default:0 }}', 'label': '已完成', 'icon': 'check', 'color': 'success'}
            ]
        elif 'teams' in path_str and 'list' in path_str:
            return [
                {'value': '{{ teams.count|default:0 }}', 'label': '团队数', 'icon': 'users', 'color': 'primary'},
                {'value': '{{ active_projects|default:0 }}', 'label': '活跃项目', 'icon': 'project-diagram', 'color': 'success'},
                {'value': '{{ team_members|default:0 }}', 'label': '团队成员', 'icon': 'user-friends', 'color': 'info'},
                {'value': '{{ pending_invites|default:0 }}', 'label': '待处理邀请', 'icon': 'envelope', 'color': 'warning'}
            ]
        elif 'boards' in path_str and 'list' in path_str:
            return [
                {'value': '{{ boards.count|default:0 }}', 'label': '看板数', 'icon': 'columns', 'color': 'primary'},
                {'value': '{{ active_boards|default:0 }}', 'label': '活跃看板', 'icon': 'eye', 'color': 'success'},
                {'value': '{{ total_cards|default:0 }}', 'label': '任务卡片', 'icon': 'sticky-note', 'color': 'info'},
                {'value': '{{ completed_cards|default:0 }}', 'label': '已完成', 'icon': 'check-circle', 'color': 'success'}
            ]
        
        return None
    
    def should_fix_template(self, file_path):
        """判断是否需要修复模板"""
        # 跳过基础模板、邮件模板、片段模板
        skip_patterns = [
            'base.html',
            'email',
            'partials',
            'includes',
            '_'
        ]
        
        path_str = str(file_path)
        for pattern in skip_patterns:
            if pattern in path_str:
                return False
        
        return True
    
    def fix_template(self, file_path):
        """修复单个模板文件"""
        if not self.should_fix_template(file_path):
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 只处理有block content的主要页面
            if 'block content' not in content:
                return
            
            print(f"修复模板: {file_path}")
            
            original_content = content
            
            # 获取页面信息
            page_info = self.get_page_info(file_path)
            stats_info = self.get_stats_info(file_path)
            
            # 1. 检查并添加页面头部
            if not re.search(r'class="page-header"', content):
                content = self.add_page_header(content, page_info)
                self.fixes_applied.append(f"{file_path}: 添加页面头部")
            
            # 2. 修复表单样式
            if '<form' in content:
                fixed_content = self.fix_form_styling(content)
                if fixed_content != content:
                    content = fixed_content
                    self.fixes_applied.append(f"{file_path}: 修复表单样式")
            
            # 3. 添加统计卡片
            if stats_info and not re.search(r'class="stats-card"', content):
                content = self.add_stats_cards(content, stats_info)
                self.fixes_applied.append(f"{file_path}: 添加统计卡片")
            
            # 只有内容发生变化时才写入文件
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ 已修复: {file_path}")
                
        except Exception as e:
            print(f"❌ 修复失败 {file_path}: {e}")
    
    def fix_all_templates(self):
        """修复所有模板文件"""
        html_files = glob.glob(str(TEMPLATES_DIR / "**" / "*.html"), recursive=True)
        
        for file_path in html_files:
            self.fix_template(file_path)
    
    def generate_report(self):
        """生成修复报告"""
        print("\n" + "="*60)
        print("🔧 UX修复报告")
        print("="*60)
        
        if not self.fixes_applied:
            print("✅ 没有需要修复的UX问题!")
            return
        
        print(f"✅ 成功应用 {len(self.fixes_applied)} 个修复:")
        for i, fix in enumerate(self.fixes_applied, 1):
            print(f"{i}. {fix}")
        
        print("\n🎯 修复完成!")

def main():
    print("🔧 开始批量UX修复...")
    
    fixer = UXFixer()
    fixer.fix_all_templates()
    fixer.generate_report()
    
    print("\n✨ UX修复完成!")

if __name__ == "__main__":
    main()
