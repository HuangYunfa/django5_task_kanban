#!/usr/bin/env python3
"""
全面的UX审查和优化脚本
对所有Django模板页面进行UX审查，确保统一的视觉层次和用户体验
"""

import os
import re
import glob
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent

# 模板目录
TEMPLATES_DIR = PROJECT_ROOT / "taskkanban" / "templates"

class UXAuditor:
    def __init__(self):
        self.issues = []
        self.fixes = []
        
    def check_page_header(self, file_path, content):
        """检查页面头部样式"""
        if not re.search(r'<div class="page-header">', content):
            if not re.search(r'class=".*?header.*?"', content):
                self.issues.append(f"{file_path}: 缺少页面头部样式")
                return False
        return True
    
    def check_stats_cards(self, file_path, content):
        """检查统计卡片样式"""
        if re.search(r'stats|统计|数据', content, re.IGNORECASE):
            if not re.search(r'class=".*?stats-card.*?"', content):
                self.issues.append(f"{file_path}: 统计数据缺少卡片样式")
                return False
        return True
    
    def check_form_styling(self, file_path, content):
        """检查表单样式"""
        if re.search(r'<form', content):
            if not re.search(r'class=".*?form-control.*?"', content):
                self.issues.append(f"{file_path}: 表单缺少Bootstrap样式")
                return False
        return True
    
    def check_button_styling(self, file_path, content):
        """检查按钮样式"""
        if re.search(r'<button|<a.*?href', content):
            if not re.search(r'class=".*?btn.*?"', content):
                self.issues.append(f"{file_path}: 按钮缺少样式")
                return False
        return True
    
    def check_responsive_design(self, file_path, content):
        """检查响应式设计"""
        if not re.search(r'col-\w+|row|container', content):
            if re.search(r'<div.*?class', content):
                self.issues.append(f"{file_path}: 缺少响应式网格布局")
                return False
        return True
    
    def audit_template(self, file_path):
        """审查单个模板文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 跳过基础模板和email模板
            if 'base.html' in str(file_path) or 'email' in str(file_path):
                return
            
            # 只检查主要页面模板
            if not any(keyword in content for keyword in ['block content', 'block main']):
                return
            
            print(f"审查模板: {file_path}")
            
            # 执行各项检查
            self.check_page_header(file_path, content)
            self.check_stats_cards(file_path, content)
            self.check_form_styling(file_path, content)
            self.check_button_styling(file_path, content)
            self.check_responsive_design(file_path, content)
            
        except Exception as e:
            print(f"处理文件 {file_path} 时出错: {e}")
    
    def audit_all_templates(self):
        """审查所有模板文件"""
        html_files = glob.glob(str(TEMPLATES_DIR / "**" / "*.html"), recursive=True)
        
        for file_path in html_files:
            self.audit_template(file_path)
    
    def generate_report(self):
        """生成审查报告"""
        print("\n" + "="*60)
        print("📋 UX审查报告")
        print("="*60)
        
        if not self.issues:
            print("✅ 所有页面UX检查通过!")
            return
        
        print(f"❌ 发现 {len(self.issues)} 个UX问题:")
        for i, issue in enumerate(self.issues, 1):
            print(f"{i}. {issue}")
        
        print("\n💡 建议修复:")
        print("1. 为主要页面添加统一的页面头部 (.page-header)")
        print("2. 为统计数据添加卡片样式 (.stats-card)")
        print("3. 确保表单使用Bootstrap样式")
        print("4. 为按钮添加适当的CSS类")
        print("5. 使用响应式网格布局")
    
    def create_ux_fixes(self):
        """创建UX修复方案"""
        print("\n🔧 生成UX修复方案...")
        
        # 生成页面头部模板
        page_header_template = '''
<!-- 页面头部 -->
<div class="page-header">
    <div class="container">
        <div class="row align-items-center">
            <div class="col-md-8">
                <h1 class="mb-0">
                    <i class="fas fa-[ICON] me-3"></i>
                    [PAGE_TITLE]
                </h1>
                <p class="lead mb-0">[PAGE_DESCRIPTION]</p>
            </div>
            <div class="col-md-4 text-md-end">
                <a href="[ACTION_URL]" class="btn btn-light btn-lg">
                    <i class="fas fa-plus me-2"></i>[ACTION_TEXT]
                </a>
            </div>
        </div>
    </div>
</div>
'''
        
        # 生成统计卡片模板
        stats_card_template = '''
<div class="row g-4 mb-5">
    <div class="col-md-3 col-6">
        <div class="card stats-card h-100">
            <div class="card-body text-center">
                <div class="stats-number text-primary">[NUMBER]</div>
                <div class="stats-label">[LABEL]</div>
                <div class="mt-3">
                    <i class="fas fa-[ICON] text-primary fa-2x"></i>
                </div>
            </div>
        </div>
    </div>
</div>
'''
        
        print("✅ UX修复模板已生成")
        
        return {
            'page_header': page_header_template,
            'stats_card': stats_card_template
        }

def main():
    print("🎨 开始全面UX审查...")
    
    auditor = UXAuditor()
    auditor.audit_all_templates()
    auditor.generate_report()
    auditor.create_ux_fixes()
    
    print("\n🎯 UX审查完成!")

if __name__ == "__main__":
    main()
