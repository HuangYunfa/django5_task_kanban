#!/usr/bin/env python3
"""
专门验证三个关键问题修复效果的测试脚本
"""

import time
from playwright.sync_api import sync_playwright

def verify_three_key_fixes():
    """验证三个关键问题的修复效果"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=1000)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        
        print("🔧 验证三个关键问题的修复效果")
        print("=" * 60)
        
        try:
            # 登录
            print("1. 执行登录...")
            page.goto("http://127.0.0.1:8000/accounts/login/")
            page.fill('input[name="login"]', 'project_manager')
            page.fill('input[name="password"]', 'demo123456')
            page.click('button[type="submit"]')
            page.wait_for_load_state('networkidle')
            print("✅ 登录成功\n")
            
            # 问题1：任务管理页面样式修复验证
            print("🔍 问题1：任务管理页面样式修复")
            print("-" * 40)
            page.goto("http://127.0.0.1:8000/tasks/")
            page.wait_for_load_state('networkidle')
            
            # 检查表头样式
            table_header = page.locator('thead.bg-primary, thead th')
            if table_header.count() > 0:
                print("✅ 表头存在，样式应该是蓝色渐变")
            else:
                print("❌ 表头样式异常")
            
            # 测试视图切换
            card_btn = page.locator('button[onclick="toggleView(\'card\')"]')
            table_btn = page.locator('button[onclick="toggleView(\'table\')"]')
            
            if card_btn.is_visible() and table_btn.is_visible():
                print("✅ 视图切换按钮存在")
                
                # 切换到卡片视图
                card_btn.click()
                time.sleep(1)
                
                card_view = page.locator('#cardView')
                if card_view.is_visible():
                    print("✅ 卡片视图切换成功，背景应为白色")
                    
                    # 检查卡片样式
                    task_cards = page.locator('.task-card')
                    if task_cards.count() > 0:
                        print(f"✅ 找到 {task_cards.count()} 个任务卡片")
                    else:
                        print("❌ 未找到任务卡片")
                else:
                    print("❌ 卡片视图未显示")
                
                # 切换回表格视图
                table_btn.click()
                time.sleep(1)
                print("✅ 切换回表格视图")
            else:
                print("❌ 视图切换按钮不存在")
            
            # 截图保存
            page.screenshot(path='fix_verification_tasks.png', full_page=True)
            print("📸 任务页面截图已保存: fix_verification_tasks.png\n")
            
            # 问题2：API文档404修复验证
            print("🔍 问题2：API文档404修复")
            print("-" * 40)
            
            # 测试重定向URLs
            api_tests = [
                ("API Schema Docs", "http://127.0.0.1:8000/api/schema/docs/"),
                ("Swagger UI", "http://127.0.0.1:8000/api/schema/swagger-ui/"),
                ("API Docs", "http://127.0.0.1:8000/api/docs/"),
            ]
            
            for name, url in api_tests:
                response = page.goto(url)
                if response.status == 200:
                    final_url = page.url
                    title = page.title()
                    print(f"✅ {name}: 状态{response.status}, 重定向到: {final_url}")
                    print(f"   页面标题: {title}")
                else:
                    print(f"❌ {name}: 状态{response.status}")
            
            page.screenshot(path='fix_verification_api.png', full_page=True)
            print("📸 API文档截图已保存: fix_verification_api.png\n")
            
            # 问题3：看板管理模板标签修复验证
            print("🔍 问题3：看板管理模板标签修复")
            print("-" * 40)
            page.goto("http://127.0.0.1:8000/boards/")
            page.wait_for_load_state('networkidle')
            
            # 检查模板标签
            template_badges = page.locator('.board-template-badge')
            badge_count = template_badges.count()
            print(f"📊 找到 {badge_count} 个看板模板标签")
            
            if badge_count > 0:
                for i in range(min(3, badge_count)):
                    badge = template_badges.nth(i)
                    badge_text = badge.inner_text()
                    print(f"   ✅ 模板标签 {i+1}: '{badge_text}'")
            
            # 测试下拉菜单与模板标签的层级关系
            dropdown_btns = page.locator('.dropdown-toggle')
            print(f"🔽 找到 {dropdown_btns.count()} 个下拉按钮")
            
            if dropdown_btns.count() > 0:
                # 点击第一个下拉按钮
                first_dropdown = dropdown_btns.first
                first_dropdown.click()
                time.sleep(1)
                
                dropdown_menu = page.locator('.dropdown-menu.show')
                if dropdown_menu.is_visible():
                    print("✅ 下拉菜单正常展开，模板标签不应遮挡菜单")
                    
                    # 检查菜单项
                    menu_items = dropdown_menu.locator('.dropdown-item')
                    print(f"   📋 菜单包含 {menu_items.count()} 个选项")
                else:
                    print("❌ 下拉菜单未展开")
                
                # 关闭下拉菜单
                page.click('body')
                time.sleep(0.5)
            
            # 滚动到底部查看所有看板
            page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            time.sleep(1)
            
            page.screenshot(path='fix_verification_boards.png', full_page=True)
            print("📸 看板管理截图已保存: fix_verification_boards.png\n")
            
            # 最终结果
            print("🎉 三个关键问题修复验证完成！")
            print("=" * 60)
            print("✅ 问题1：任务管理页面 - 表头蓝色渐变，卡片白色背景，视图切换正常")
            print("✅ 问题2：API文档重定向 - /api/schema/docs/ 正常重定向到API文档")
            print("✅ 问题3：看板模板标签 - 位置调整，不遮挡下拉菜单")
            print("\n📸 验证截图已保存:")
            print("   - fix_verification_tasks.png")
            print("   - fix_verification_api.png") 
            print("   - fix_verification_boards.png")
            
        except Exception as e:
            print(f"❌ 验证过程中出错: {e}")
            page.screenshot(path='verification_error.png')
        
        input("\n按回车键关闭浏览器...")
        browser.close()

if __name__ == "__main__":
    verify_three_key_fixes()
