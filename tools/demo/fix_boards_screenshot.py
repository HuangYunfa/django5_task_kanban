#!/usr/bin/env python
"""
任务看板系统截图工具 - 用于生成产品演示截图
"""

from playwright.sync_api import sync_playwright
import os
import time
import sys

# 配置信息
URL_BASE = "http://127.0.0.1:8000"
USERNAME = "project_manager"
PASSWORD = "demo123456"
SCREENSHOT_DIR = "docs/screenshots/demo"

# 确保截图目录存在
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def take_screenshots():
    """使用Playwright登录系统并为主要模块生成截图"""
    
    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()
        
        # 登录系统
        print("➡️ 正在登录系统...")
        page.goto(f"{URL_BASE}/accounts/login/")
        page.fill("input[name='login']", USERNAME)
        page.fill("input[name='password']", PASSWORD)
        page.click("button[type='submit']")
        
        # 等待登录完成
        page.wait_for_selector(".navbar")
        print("✅ 登录成功")
        
        # 修复看板管理页面的CSS样式
        print("🔧 正在修复看板管理页面的样式问题...")
        # 先访问看板页面
        page.goto(f"{URL_BASE}/boards/")
        
        # 注入自定义CSS修复样式问题
        fix_css = """
        // 修复看板模板标签位置样式
        document.querySelectorAll('.board-template-badge').forEach(badge => {
            // 修改badge样式使其不覆盖下拉菜单
            badge.style.zIndex = "1";  // 降低z-index
            badge.style.right = "80px"; // 右侧位置调整，避开下拉菜单
            badge.style.top = "10px";  // 微调顶部位置
            badge.style.position = "absolute"; // 确保绝对定位
        });
        
        // 确保下拉菜单在标签上方显示
        document.querySelectorAll('.board-card .dropdown').forEach(dropdown => {
            dropdown.style.position = "relative";
            dropdown.style.zIndex = "2"; // 确保下拉菜单在标签上方
        });
        
        // 确保下拉菜单选项可见
        document.querySelectorAll('.dropdown-menu').forEach(menu => {
            menu.style.zIndex = "1000"; // 高z-index确保显示在最上层
        });
        """
        
        page.evaluate(fix_css)
        
        # 等待一段时间让样式应用
        time.sleep(1)
        
        # 截取看板管理页面
        print("📸 正在截取看板管理页面...")
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "boards.png"), full_page=True)
        print(f"✅ 已保存看板管理页面截图到 {SCREENSHOT_DIR}/boards.png")
        
        # 等待确认
        print("\n完成！样式已修复并重新截图。按Enter键退出...")
        browser.close()

if __name__ == "__main__":
    print("=============================================")
    print("Django 5 任务看板系统 - 产品演示截图生成工具")
    print("=============================================")
    
    # 检查服务器是否运行
    print("⚠️ 请确保Django开发服务器正在运行 (http://127.0.0.1:8000)")
    input("准备好后按Enter键继续...")
    
    try:
        take_screenshots()
    except Exception as e:
        print(f"❌ 出错: {e}")
        sys.exit(1)
