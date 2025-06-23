"""
快速验证6个关键修复的脚本
用于确认所有修复都已正确应用
"""

import re
import os

def check_file_content(file_path, search_patterns, description):
    """检查文件内容是否包含指定模式"""
    print(f"\n检查 {description}:")
    print(f"文件: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"   ❌ 文件不存在")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    all_found = True
    for pattern, desc in search_patterns:
        if pattern in content:
            print(f"   ✅ {desc}")
        else:
            print(f"   ❌ {desc}")
            all_found = False
    
    return all_found

def main():
    """主验证函数"""
    print("🚀 验证6个关键问题修复情况")
    print("="*50)
    
    base_path = r"d:\Learning\python_dev\django_template\django5_task_kanban\taskkanban"
    
    # 检查1: 登录页面样式修复
    login_html = os.path.join(base_path, "templates", "account", "login.html")
    check_file_content(login_html, [
        ("box-sizing: border-box", "包含box-sizing样式修复")
    ], "登录页面样式修复")
    
    # 检查2: 注册页面样式修复
    signup_html = os.path.join(base_path, "templates", "account", "signup.html")
    check_file_content(signup_html, [
        ("box-sizing: border-box", "包含box-sizing样式修复")
    ], "注册页面样式修复")
    
    # 检查3: 忘记密码页面样式
    reset_html = os.path.join(base_path, "templates", "account", "password_reset.html")
    check_file_content(reset_html, [
        ("auth-container", "包含auth-container样式"),
        ("box-sizing: border-box", "包含box-sizing样式")
    ], "忘记密码页面样式")
    
    # 检查4: 团队详情页dashboard修复
    team_detail_html = os.path.join(base_path, "templates", "teams", "detail.html")
    check_file_content(team_detail_html, [
        ("reports:index", "使用正确的reports:index URL")
    ], "团队详情页dashboard修复")
    
    # 检查5: API URLs修复
    api_urls = os.path.join(base_path, "api", "urls.py")
    check_file_content(api_urls, [
        ("schema/swagger-ui/", "包含schema/swagger-ui重定向"),
        ("RedirectView", "包含重定向视图")
    ], "API Schema Swagger UI修复")
    
    # 检查6: 切换账号功能修复
    users_views = os.path.join(base_path, "users", "views.py")
    check_file_content(users_views, [
        ("class SwitchAccountView", "包含SwitchAccountView类"),
        ("logout(request)", "包含logout逻辑")
    ], "用户视图切换账号修复")
    
    users_urls = os.path.join(base_path, "users", "urls.py")
    check_file_content(users_urls, [
        ("switch-account/", "包含switch-account URL"),
        ("SwitchAccountView", "引用SwitchAccountView")
    ], "用户URLs切换账号修复")
    
    base_html = os.path.join(base_path, "templates", "base.html")
    check_file_content(base_html, [
        ("users:switch_account", "使用正确的切换账号URL")
    ], "基础模板切换账号修复")
    
    print("\n" + "="*50)
    print("🎉 验证完成！")
    print("请手动测试以下URL以确认修复效果：")
    print("1. http://127.0.0.1:8000/accounts/login/")
    print("2. http://127.0.0.1:8000/accounts/signup/")
    print("3. http://127.0.0.1:8000/accounts/password/reset/")
    print("4. http://127.0.0.1:8000/teams/[团队ID]/")
    print("5. http://127.0.0.1:8000/api/schema/swagger-ui/")
    print("6. 点击用户下拉菜单中的'切换账号'")

if __name__ == '__main__':
    main()
