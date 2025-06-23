#!/usr/bin/env python
"""
自动化测试脚本 - 登录并生成产品演示截图
"""

import os
import time
from playwright.sync_api import sync_playwright

# 确保screenshots目录存在
SCREENSHOTS_DIR = "demo_screenshots"
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

# 登录信息
LOGIN_URL = "http://127.0.0.1:8000/users/login/"
USERNAME = "project_manager"
PASSWORD = "demo123456"

# 需要截图的页面列表
PAGES_TO_CAPTURE = [
    {"url": "/", "name": "homepage", "title": "首页"},
    {"url": "/dashboard/", "name": "dashboard", "title": "工作台"},
    {"url": "/boards/", "name": "boards", "title": "看板管理"},
    {"url": "/tasks/", "name": "tasks", "title": "任务管理"},
    {"url": "/teams/", "name": "teams", "title": "团队管理"},
    {"url": "/reports/", "name": "reports", "title": "报表分析"},
    {"url": "/api/schema/swagger-ui/", "name": "api_docs", "title": "API文档"},
    {"url": "/users/profile/", "name": "user_profile", "title": "用户资料"},
]

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
        # 先检查实际的表单字段
        print("分析登录表单...")
        form_html = page.content()
        print(f"当前页面URL: {page.url}")
        
        # 尝试不同的可能字段名
        for username_field in ['input[name="login"]', 'input[name="username"]', 'input[id="id_username"]', 'input[id="id_login"]']:
            if page.locator(username_field).count() > 0:
                print(f"找到用户名字段: {username_field}")
                page.fill(username_field, USERNAME)
                break
                
        for password_field in ['input[name="password"]', 'input[id="id_password"]']:
            if page.locator(password_field).count() > 0:
                print(f"找到密码字段: {password_field}")
                page.fill(password_field, PASSWORD)
                break
                
        # 查找提交按钮
        submit_buttons = ['button[type="submit"]', 'input[type="submit"]', 'button:has-text("登录")']
        for btn in submit_buttons:
            if page.locator(btn).count() > 0:
                print(f"找到提交按钮: {btn}")
                page.click(btn)
                break
        
        # 等待登录完成
        page.wait_for_load_state("networkidle")
        time.sleep(2)  # 额外等待确保完全加载
        
        if "login" in page.url:
            print("❌ 登录失败，请检查用户名和密码")
            browser.close()
            return
        
        print("✅ 登录成功！")
        
        # 遍历所有页面并截图
        for page_info in PAGES_TO_CAPTURE:
            page_url = f"http://127.0.0.1:8000{page_info['url']}"
            screenshot_path = os.path.join(SCREENSHOTS_DIR, f"{page_info['name']}.png")
            
            print(f"正在访问 {page_info['title']} ({page_url})...")
            page.goto(page_url)
            page.wait_for_load_state("networkidle")
            time.sleep(1)  # 额外等待确保完全加载
            
            # 截图
            print(f"正在截图: {screenshot_path}")
            page.screenshot(path=screenshot_path, full_page=True)
        
        # 演示一个看板的详细视图 (假设有一个看板)
        try:
            print("尝试访问一个看板详情...")
            page.goto("http://127.0.0.1:8000/boards/")
            page.wait_for_load_state("networkidle")
            
            # 点击第一个看板的查看链接
            board_links = page.query_selector_all('a.btn-primary:has-text("查看")')
            if board_links and len(board_links) > 0:
                board_links[0].click()
                page.wait_for_load_state("networkidle")
                time.sleep(1)
                
                # 截图看板详情页
                board_detail_path = os.path.join(SCREENSHOTS_DIR, "board_detail.png")
                print(f"正在截图看板详情: {board_detail_path}")
                page.screenshot(path=board_detail_path, full_page=True)
        except Exception as e:
            print(f"无法访问看板详情: {e}")
        
        # 关闭浏览器
        browser.close()
        print(f"\n✅ 截图完成！所有截图已保存到 {SCREENSHOTS_DIR} 目录")

if __name__ == "__main__":
    main()
