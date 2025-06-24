#!/usr/bin/env python
"""
批量修复移动后的测试脚本路径问题
"""
import os
import re
from pathlib import Path

def fix_django_setup_paths():
    """修复Django setup路径配置"""
    
    # 需要修复的目录
    directories_to_fix = [
        'tests/integration/email',
        'tests/unit',
        'tests/ui',
        'tests/api',
        'tools/utilities',
        'tools/debug',
        'tools/fixes',
        'tools/analysis'
    ]
    
    fixed_count = 0
    
    for directory in directories_to_fix:
        if not os.path.exists(directory):
            continue
            
        print(f"\n🔧 修复目录: {directory}")
        
        for filename in os.listdir(directory):
            if not filename.endswith('.py') or filename == '__init__.py':
                continue
                
            filepath = os.path.join(directory, filename)
            
            # 读取文件内容
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                print(f"❌ 读取文件失败 {filepath}: {e}")
                continue
            
            # 检查是否需要修复Django路径
            if 'django.setup()' in content and 'project_root = Path(__file__).parent' in content:
                # 计算相对于项目根目录的层级
                relative_path = os.path.relpath(filepath, '.')
                depth = len(Path(relative_path).parts) - 1
                
                if depth > 0:
                    # 构建正确的路径
                    parent_parts = '.parent' * depth
                    new_path_line = f"project_root = Path(__file__){parent_parts} / 'taskkanban'"
                    
                    # 替换路径配置
                    old_pattern = r"project_root = Path\(__file__\)\.parent.*? / 'taskkanban'"
                    if re.search(old_pattern, content):
                        new_content = re.sub(old_pattern, new_path_line, content)
                        
                        # 写入修复后的内容
                        try:
                            with open(filepath, 'w', encoding='utf-8') as f:
                                f.write(new_content)
                            print(f"✅ 修复: {filename}")
                            fixed_count += 1
                        except Exception as e:
                            print(f"❌ 写入文件失败 {filepath}: {e}")
                    else:
                        print(f"⚠️  未找到预期的路径配置模式: {filename}")
            
    print(f"\n🎉 完成！共修复了 {fixed_count} 个文件")
    return fixed_count

def create_template_scripts():
    """创建模板脚本，用于正确的Django配置"""
    
    template_content = '''#!/usr/bin/env python
"""
测试脚本模板 - 正确的Django配置
"""
import os
import sys
import django
from pathlib import Path

# 添加项目根目录到Python路径 - 根据脚本位置自动计算
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent / 'taskkanban'  # 根据实际层级调整
sys.path.insert(0, str(project_root))

# 设置Django设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskkanban.settings')
django.setup()

# 在这里添加你的测试代码
if __name__ == '__main__':
    print("Django setup 成功!")
    print(f"项目根目录: {project_root}")
    print(f"脚本位置: {__file__}")
'''
    
    template_path = 'tools/utilities/django_test_template.py'
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    print(f"✅ 创建了测试脚本模板: {template_path}")

def main():
    """主函数"""
    print("=== 批量修复测试脚本路径问题 ===")
    
    # 修复现有脚本
    fixed_count = fix_django_setup_paths()
    
    # 创建模板脚本
    create_template_scripts()
    
    if fixed_count > 0:
        print(f"\n💡 建议:")
        print(f"   1. 测试修复后的脚本是否能正常运行")
        print(f"   2. 如有问题，请参考模板脚本调整路径配置") 
        print(f"   3. 对于复杂的测试，建议使用 pytest 运行")

if __name__ == "__main__":
    main()
