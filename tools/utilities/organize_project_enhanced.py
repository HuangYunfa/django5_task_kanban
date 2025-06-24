#!/usr/bin/env python
"""
Django项目文件结构整理工具（改进版）
根据项目结构规范，将散落在根目录的测试文件和工具脚本整理到合适的目录
"""
import os
import shutil
import re
from datetime import datetime
from pathlib import Path

def organize_test_and_tool_files():
    """整理项目根目录下的测试文件和工具脚本"""
    
    print("=== Django项目文件结构整理 ===")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 定义移动规则 - 按优先级排列
    move_rules = [
        # 特殊脚本规则
        {"pattern": r"reset_.*password.*\.py", "target_dir": "tools/utilities/", "description": "密码重置工具"},
        {"pattern": r"verify_success_check\.py", "target_dir": "tools/utilities/", "description": "验证检查工具"},
        
        # 邮件验证测试文件
        {"pattern": r"test_email.*\.py|test_.*email.*\.py|test_smtp.*\.py|test_custom.*\.py", "target_dir": "tests/integration/email/", "description": "邮件系统集成测试"},
        
        # API测试文件
        {"pattern": r"test_api_.*\.py", "target_dir": "tests/api/", "description": "API接口测试"},
        
        # UI测试文件
        {"pattern": r"test_ui_.*\.py|test_.*ui\.py|test_frontend.*\.py|test_full_ui.*\.py|test_ux.*\.py", "target_dir": "tests/ui/", "description": "UI界面测试"},
        
        # 集成测试文件
        {"pattern": r"test_.*integration.*\.py|test_batch.*\.py", "target_dir": "tests/integration/", "description": "集成测试"},
        
        # 单元测试文件
        {"pattern": r"test_board.*\.py|test_task.*\.py|test_team.*\.py|test_user.*\.py|test_workflow.*\.py", "target_dir": "tests/unit/", "description": "单元测试"},
        {"pattern": r"test_.*\.py", "target_dir": "tests/unit/", "description": "通用单元测试"},
        
        # 调试文件规则
        {"pattern": r"debug_.*\.py", "target_dir": "tools/debug/", "description": "调试工具"},
        
        # 修复文件规则
        {"pattern": r"fix_.*\.py|.*fix.*\.py", "target_dir": "tools/fixes/", "description": "修复工具"},
        
        # 验证文件规则
        {"pattern": r"verify.*\.py|.*verification.*\.py", "target_dir": "tools/utilities/", "description": "验证工具"},
        
        # 分析文件规则
        {"pattern": r"analyze.*\.py|.*analysis.*\.py|check.*\.py|.*report.*\.py", "target_dir": "tools/analysis/", "description": "分析工具"},
        
        # 规划文件规则
        {"pattern": r".*roadmap.*\.py|.*plan.*\.py|next_.*\.py", "target_dir": "tools/planning/", "description": "规划工具"},
        
        # 演示文件规则
        {"pattern": r"create_.*_demo\.py|demo_.*\.py", "target_dir": "tools/demo/", "description": "演示工具"},
    ]
    
    # 跳过的文件
    skip_files = {
        'manage.py',
        'organize_project_enhanced.py',  # 当前脚本
        '__init__.py'
    }
    
    # 移动文件计数
    moved_count = 0
    error_count = 0
    skipped_count = 0
    
    # 移动详情记录
    move_details = []
    
    print("\n🔍 扫描根目录中的Python文件...")
    
    # 遍历根目录中的所有Python文件
    for filename in sorted(os.listdir('.')):
        if not filename.endswith('.py'):
            continue
        
        # 跳过特殊文件
        if filename in skip_files:
            print(f"⏭️  跳过: {filename} (特殊文件)")
            skipped_count += 1
            continue
        
        # 跳过已在正确目录的文件
        if '/' in filename or '\\' in filename:
            continue
            
        # 匹配规则
        target_dir = None
        rule_description = None
        
        for rule in move_rules:
            if re.match(rule["pattern"], filename, re.IGNORECASE):
                target_dir = rule["target_dir"]
                rule_description = rule["description"]
                break
        
        # 如果没有匹配到规则，默认放入tools/utilities目录
        if not target_dir:
            target_dir = "tools/utilities/"
            rule_description = "通用工具"
        
        # 确保目标目录存在
        os.makedirs(target_dir, exist_ok=True)
        
        # 移动文件
        source_path = os.path.join('.', filename)
        target_path = os.path.join(target_dir, filename)
        
        # 检查目标文件是否已存在
        if os.path.exists(target_path):
            print(f"⚠️  文件已存在: {target_path}")
            backup_path = target_path + '.backup'
            if os.path.exists(backup_path):
                os.remove(backup_path)
            shutil.move(target_path, backup_path)
            print(f"   备份原文件为: {backup_path}")
        
        try:
            print(f"📦 移动: {source_path} -> {target_path} ({rule_description})")
            shutil.move(source_path, target_path)
            moved_count += 1
            move_details.append({
                'file': filename,
                'source': source_path,
                'target': target_path,
                'category': rule_description
            })
        except Exception as e:
            print(f"❌ 移动文件 {filename} 失败: {e}")
            error_count += 1
    
    # 处理截图文件
    handle_screenshots()
    
    # 创建README文件
    create_readme_files()
    
    # 显示统计结果
    print_summary(moved_count, error_count, skipped_count, move_details)
    
    return moved_count > 0

def handle_screenshots():
    """处理截图文件"""
    print("\n📸 处理截图文件...")
    
    if os.path.exists('screenshots') and os.path.isdir('screenshots'):
        screenshots_dir = 'tests/screenshots'
        os.makedirs(screenshots_dir, exist_ok=True)
        
        moved_images = 0
        for filename in os.listdir('screenshots'):
            source_path = os.path.join('screenshots', filename)
            target_path = os.path.join(screenshots_dir, filename)
            
            try:
                print(f"📦 移动: {source_path} -> {target_path}")
                shutil.move(source_path, target_path)
                moved_images += 1
            except Exception as e:
                print(f"❌ 移动文件 {filename} 失败: {e}")
        
        print(f"✅ 移动了 {moved_images} 个截图文件")
        
        # 尝试删除空的screenshots目录
        try:
            if len(os.listdir('screenshots')) == 0:
                os.rmdir('screenshots')
                print("🗑️  删除了空的screenshots目录")
        except Exception as e:
            print(f"❌ 删除screenshots目录失败: {e}")
    else:
        print("📸 未发现screenshots目录")

def create_readme_files():
    """为各个目录创建或更新README.md文件"""
    print("\n📝 创建/更新README文件...")
    
    readme_templates = {
        'tests/integration/email': """# 邮件系统集成测试

本目录包含邮件系统相关的集成测试文件，主要测试：

## 测试内容

1. **邮件发送功能测试**
   - SMTP配置测试
   - 邮件后端测试
   - 邮件发送流程测试

2. **邮箱验证功能测试**
   - 验证邮件发送
   - 验证链接生成
   - 验证流程完整性

3. **邮件模板测试**
   - HTML邮件模板
   - 纯文本邮件模板
   - 邮件内容渲染

## 运行测试

```bash
# 运行所有邮件集成测试
pytest tests/integration/email/ -v

# 运行特定测试文件
python tests/integration/email/test_email_verification.py
```

## 配置要求

测试运行前需要确保邮件配置正确：
- Django settings中的EMAIL_BACKEND
- SMTP服务器配置（如使用真实SMTP）
- 测试用户和邮箱地址

## 注意事项

- 部分测试需要真实的SMTP服务器
- 测试过程中可能发送真实邮件，请使用测试邮箱
- console后端测试不会发送真实邮件
""",
        
        'tools/utilities': """# 项目工具实用程序

本目录包含用于项目管理和维护的各种实用工具脚本。

## 工具分类

### 🔧 系统管理工具
- `reset_superuser_password.py` - 超级用户密码重置工具
- `verify_success_check.py` - 系统状态验证工具

### 📁 项目管理工具
- `organize_project.py` - 项目文件结构整理工具
- `organize_project_enhanced.py` - 改进版项目整理工具

### 🔍 验证工具
- `verify_*.py` - 各类功能验证脚本

## 使用方式

```bash
# 重置超级用户密码
python tools/utilities/reset_superuser_password.py

# 整理项目文件结构
python tools/utilities/organize_project_enhanced.py

# 验证系统状态
python tools/utilities/verify_success_check.py
```

## 注意事项

- 这些工具主要用于开发和维护，而非日常业务功能
- 部分工具可能修改数据库或文件结构，使用前请备份
- 建议在测试环境中先验证工具功能
"""
    }
    
    for dir_path, content in readme_templates.items():
        if os.path.exists(dir_path):
            readme_path = os.path.join(dir_path, 'README.md')
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 创建/更新了 {readme_path}")

def print_summary(moved_count, error_count, skipped_count, move_details):
    """打印整理结果摘要"""
    print(f"\n{'='*50}")
    print("📊 整理结果摘要")
    print(f"{'='*50}")
    print(f"✅ 成功移动: {moved_count} 个文件")
    print(f"⏭️  跳过文件: {skipped_count} 个文件")
    print(f"❌ 移动失败: {error_count} 个文件")
    
    if move_details:
        print(f"\n📋 移动详情:")
        categories = {}
        for detail in move_details:
            category = detail['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(detail['file'])
        
        for category, files in categories.items():
            print(f"\n📂 {category}:")
            for file in files:
                print(f"   • {file}")
    
    print(f"\n⏰ 完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if moved_count > 0:
        print(f"\n🎉 项目文件结构整理完成！")
        print(f"📁 测试文件已整理到 tests/ 目录")
        print(f"🔧 工具脚本已整理到 tools/ 目录")
        print(f"📚 相关README文件已创建/更新")
        
        # 提供后续建议
        print(f"\n💡 后续建议:")
        print(f"   1. 运行 pytest 验证测试文件是否正常")
        print(f"   2. 检查工具脚本是否可以正常执行")
        print(f"   3. 更新项目文档中的文件路径引用")
        print(f"   4. 提交这些结构调整到版本控制")
    else:
        print(f"\n✨ 项目文件结构已经很整洁！")

def verify_project_structure():
    """验证项目结构是否正确"""
    print(f"\n🔍 验证项目结构...")
    
    required_dirs = [
        'tests/ui',
        'tests/unit', 
        'tests/integration',
        'tests/api',
        'tools/utilities',
        'tools/debug',
        'tools/fixes',
        'tools/analysis',
        'docs'
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print(f"⚠️  缺少以下目录:")
        for dir_path in missing_dirs:
            print(f"   • {dir_path}")
            os.makedirs(dir_path, exist_ok=True)
            print(f"   ✅ 已创建: {dir_path}")
    else:
        print(f"✅ 项目目录结构完整")

def main():
    """主函数"""
    # 确保在项目根目录执行
    if not os.path.exists('taskkanban') or not os.path.exists('README.md'):
        print("❌ 请在Django项目根目录执行此脚本！")
        return False
    
    # 验证项目结构
    verify_project_structure()
    
    # 执行文件整理
    success = organize_test_and_tool_files()
    
    return success

if __name__ == "__main__":
    main()
