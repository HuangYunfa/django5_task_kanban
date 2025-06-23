#!/usr/bin/env python
"""
看板管理页面卡片样式优化脚本
"""

import time
from playwright.sync_api import sync_playwright

# 登录信息
LOGIN_URL = "http://127.0.0.1:8000/users/login/"
USERNAME = "project_manager"
PASSWORD = "demo123456"

# 改进的CSS样式
IMPROVED_CARD_STYLE = """
/* 注入优化的看板卡片样式 */
.board-card {
    border-radius: 12px;
    overflow: hidden;
    transition: all 0.3s ease;
    box-shadow: 0 3px 10px rgba(0,0,0,0.08);
    border: none;
    position: relative;
}

.board-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 20px rgba(0,0,0,0.12);
}

.board-card .card-header {
    background: linear-gradient(135deg, #6a82fb 0%, #4364f7 100%);
    color: white;
    border-bottom: none;
    padding: 15px 20px;
}

.board-card .card-title {
    font-weight: 600;
    margin: 0;
}

.board-card .card-title a {
    color: white;
    text-decoration: none;
}

.board-card .card-body {
    padding: 20px;
    background-color: #fff;
}

.board-card .card-footer {
    background-color: #f8f9fa;
    border-top: none;
    padding: 15px 20px;
}

/* 移除模板标签，改用其他方式显示 */
.board-template-badge {
    position: static;
    display: inline-block;
    margin-top: 10px;
    margin-bottom: 5px;
    background: rgba(66, 133, 244, 0.15);
    color: #4285f4;
    font-weight: 600;
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 0.8rem;
}

/* 改进看板统计样式 */
.board-stats {
    margin-top: 15px;
}

.board-stats .stat {
    display: flex;
    align-items: center;
    margin-bottom: 10px;
    color: #555;
}

.board-stats .stat i {
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(66, 133, 244, 0.1);
    color: #4285f4;
    border-radius: 50%;
    margin-right: 10px;
}

/* 改进按钮样式 */
.board-card .btn-primary {
    background: #4285f4;
    border-color: #4285f4;
    padding: 8px 16px;
    border-radius: 6px;
}

.board-card .btn-outline-secondary {
    border-color: #ddd;
    color: #555;
    padding: 8px 16px;
    border-radius: 6px;
}

.board-card .btn-primary:hover,
.board-card .btn-primary:focus {
    background: #3367d6;
    border-color: #3367d6;
}

.board-card .dropdown-toggle {
    background: transparent;
    color: white;
    border: none;
    padding: 0;
    box-shadow: none;
}

.board-card .dropdown-toggle:hover,
.board-card .dropdown-toggle:focus {
    background: rgba(255,255,255,0.1);
}

/* 卡片描述文本 */
.board-card .card-text {
    color: #666;
    margin-bottom: 15px;
    font-size: 0.95rem;
    line-height: 1.5;
}
"""

def main():
    with sync_playwright() as p:
        # 启动浏览器
        print("启动浏览器...")
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()
        
        # 登录系统
        print(f"正在登录系统 ({USERNAME})...")
        page.goto(LOGIN_URL)
        
        # 查找用户名和密码字段
        for username_field in ['input[name="username"]', 'input[id="id_username"]']:
            if page.locator(username_field).count() > 0:
                page.fill(username_field, USERNAME)
                break
                
        for password_field in ['input[name="password"]', 'input[id="id_password"]']:
            if page.locator(password_field).count() > 0:
                page.fill(password_field, PASSWORD)
                break
                
        # 查找提交按钮
        for btn in ['button[type="submit"]', 'input[type="submit"]']:
            if page.locator(btn).count() > 0:
                page.click(btn)
                break
        
        # 等待登录完成
        page.wait_for_load_state("networkidle")
        time.sleep(1)
        
        # 访问看板管理页面
        print("正在访问看板管理页面...")
        page.goto("http://127.0.0.1:8000/boards/")
        page.wait_for_load_state("networkidle")
        
        # 注入自定义CSS样式
        print("注入优化的CSS样式...")
        page.add_style_tag(content=IMPROVED_CARD_STYLE)
        
        # 等待样式应用
        time.sleep(1)
        
        # 截图
        print("正在截图看板管理页面...")
        screenshot_path = "docs/screenshots/demo/boards.png"
        page.screenshot(path=screenshot_path, full_page=True)
        
        print(f"✅ 截图完成！已保存到 {screenshot_path}")
        
        # 关闭浏览器
        browser.close()

if __name__ == "__main__":
    main()
