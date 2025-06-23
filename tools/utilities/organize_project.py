import os
import shutil
import re
from datetime import datetime

def organize_files():
    """整理项目根目录下的Python文件到指定目录"""
    
    # 定义移动规则
    move_rules = [
        # 测试文件规则
        {"pattern": r"test_api_.*\.py", "target_dir": "tests/api/"},
        {"pattern": r"test_ui_.*\.py|test_.*ui\.py|test_frontend.*\.py|test_full_ui\.py|test_ux.*\.py", "target_dir": "tests/ui/"},
        {"pattern": r"test_.*integration.*\.py", "target_dir": "tests/integration/"},
        {"pattern": r"test_board.*\.py|test_task.*\.py|test_team.*\.py|test_user.*\.py|test_workflow.*\.py", "target_dir": "tests/unit/"},
        {"pattern": r"test_.*\.py", "target_dir": "tests/unit/"},  # 其他测试默认放入单元测试
        
        # 调试文件规则
        {"pattern": r"debug_.*\.py", "target_dir": "tools/debug/"},
        
        # 修复文件规则
        {"pattern": r"fix_.*\.py|.*fix.*\.py|verify.*\.py", "target_dir": "tools/fixes/"},
        
        # 分析文件规则
        {"pattern": r"analyze.*\.py|.*analysis.*\.py|check.*\.py|.*report.*\.py", "target_dir": "tools/analysis/"},
        
        # 规划文件规则
        {"pattern": r".*roadmap.*\.py|.*plan.*\.py|next_.*\.py", "target_dir": "tools/planning/"},
        
        # 演示文件规则
        {"pattern": r"create_.*_demo\.py|demo_.*\.py", "target_dir": "tools/demo/"},
    ]
    
    # 移动文件计数
    moved_count = 0
    error_count = 0
    
    # 遍历根目录中的所有Python文件
    for filename in os.listdir('.'):
        if not filename.endswith('.py') or filename == 'manage.py':
            continue
        
        # 跳过特殊文件和目录
        if filename == os.path.basename(__file__):  # 跳过当前脚本自身
            continue
            
        # 匹配规则
        target_dir = None
        for rule in move_rules:
            if re.match(rule["pattern"], filename, re.IGNORECASE):
                target_dir = rule["target_dir"]
                break
        
        # 如果没有匹配到规则，默认放入tools/utilities目录
        if not target_dir:
            target_dir = "tools/utilities/"
        
        # 确保目标目录存在
        os.makedirs(target_dir, exist_ok=True)
        
        # 移动文件
        source_path = os.path.join('.', filename)
        target_path = os.path.join(target_dir, filename)
        
        try:
            print(f"移动 {source_path} -> {target_path}")
            shutil.move(source_path, target_path)
            moved_count += 1
        except Exception as e:
            print(f"❌ 移动文件 {filename} 失败: {e}")
            error_count += 1
    
    print(f"\n✅ 完成！成功移动 {moved_count} 个文件，{error_count} 个错误")
    
    # 处理截图文件
    if os.path.exists('screenshots') and os.path.isdir('screenshots'):
        print("\n处理截图文件...")
        screenshots_dir = 'tests/screenshots'
        os.makedirs(screenshots_dir, exist_ok=True)
        
        moved_images = 0
        for filename in os.listdir('screenshots'):
            source_path = os.path.join('screenshots', filename)
            target_path = os.path.join(screenshots_dir, filename)
            
            try:
                print(f"移动 {source_path} -> {target_path}")
                shutil.move(source_path, target_path)
                moved_images += 1
            except Exception as e:
                print(f"❌ 移动文件 {filename} 失败: {e}")
        
        print(f"✅ 移动了 {moved_images} 个截图文件")
        
        # 尝试删除空的screenshots目录
        try:
            if len(os.listdir('screenshots')) == 0:
                os.rmdir('screenshots')
                print("✅ 删除了空的screenshots目录")
        except Exception as e:
            print(f"❌ 删除screenshots目录失败: {e}")
    
def create_readme_files():
    """为各个目录创建README.md文件"""
    
    readme_templates = {
        'tests/screenshots': """# 测试截图目录

本目录包含项目测试过程中产生的各类截图，主要用于：

1. **UI测试验证**：记录UI测试过程中的界面状态
2. **问题记录**：捕获和记录各类UI问题
3. **修复前后对比**：展示修复前后的UI差异
4. **调试过程记录**：展示调试过程中的关键步骤

## 截图分类

- `debug_*.png` - 调试过程截图
- `fix*_*.png` - 修复效果截图
- `issue*_*.png` - 问题记录截图
- `*_verification_*.png` - 验证测试截图
- `responsive_*.png` - 响应式设计测试截图
- `*Dropdown_*.png` - 下拉菜单测试截图

这些截图主要配合tests/ui目录下的UI测试脚本使用，用于验证UI功能的正确性和记录修复过程。
""",
        'tools/utilities': """# 项目工具实用程序

本目录包含用于项目管理和维护的各种实用工具脚本。

## 工具列表

- `organize_project.py` - 项目文件结构整理工具，用于按功能和类型整理项目文件

这些工具主要用于项目维护和管理，而非日常开发过程。
"""
    }
    
    for dir_path, content in readme_templates.items():
        if os.path.exists(dir_path):
            readme_path = os.path.join(dir_path, 'README.md')
            if not os.path.exists(readme_path):
                with open(readme_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ 创建了 {readme_path}")

if __name__ == "__main__":
    # 保存当前工作目录
    original_dir = os.getcwd()
    
    try:
        # 确保在项目根目录执行脚本
        project_root = os.path.abspath('.')
        os.chdir(project_root)
        
        print(f"开始整理项目文件... ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
        organize_files()
        create_readme_files()
        print(f"项目整理完成！({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
    finally:
        # 恢复原始工作目录
        os.chdir(original_dir)
