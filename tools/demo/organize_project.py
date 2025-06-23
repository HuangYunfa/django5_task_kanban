import os
import shutil
import re

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
    ]
    
    # 移动文件计数
    moved_count = 0
    error_count = 0
    
    # 遍历根目录中的所有Python文件
    for filename in os.listdir('.'):
        if not filename.endswith('.py') or filename == 'manage.py':
            continue
        
        # 跳过特殊文件和目录
        if filename == 'organize_project.py':  # 跳过当前脚本自身
            continue
            
        # 匹配规则
        target_dir = None
        for rule in move_rules:
            if re.match(rule["pattern"], filename, re.IGNORECASE):
                target_dir = rule["target_dir"]
                break
        
        # 如果没有匹配到规则，默认放入tools目录
        if not target_dir:
            target_dir = "tools/"
        
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
    
if __name__ == "__main__":
    # 保存当前工作目录
    original_dir = os.getcwd()
    
    try:
        # 确保在项目根目录执行脚本
        project_root = os.path.abspath('.')
        os.chdir(project_root)
        
        print("开始整理项目文件...")
        organize_files()
    finally:
        # 恢复原始工作目录
        os.chdir(original_dir)
