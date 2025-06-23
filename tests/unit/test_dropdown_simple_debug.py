#!/usr/bin/env python3
"""
简单的下拉菜单调试测试脚本
专门测试点击打开/关闭的基础功能
"""

import time
import sys
import os
from playwright.sync_api import sync_playwright, expect

def test_dropdown_simple_debug():
    """简单测试下拉菜单的基础点击功能"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context()
        page = context.new_page()
        
        print("=" * 50)
        print("简单下拉菜单调试测试")
        print("=" * 50)
        
        try:
            # 1. 登录系统
            print("\n🔐 执行登录...")
            page.goto("http://127.0.0.1:8000/accounts/login/")
            page.fill("input[name='login']", "project_manager")
            page.fill("input[name='password']", "demo123456")
            page.click("button[type='submit']")
            page.wait_for_url("**/dashboard/")
            print("✅ 登录成功")
            
            # 2. 测试用户下拉菜单多次点击
            print("\n🔍 测试用户下拉菜单...")
            
            for i in range(5):
                print(f"\n--- 第 {i+1} 次点击用户下拉菜单 ---")
                
                # 点击前状态
                before_state = page.evaluate("""
                    () => {
                        const trigger = document.getElementById('userDropdown');
                        const menu = trigger ? trigger.nextElementSibling : null;
                        
                        return {
                            triggerExists: !!trigger,
                            menuExists: !!menu,
                            menuHasShow: menu ? menu.classList.contains('show') : false,
                            menuDisplay: menu ? window.getComputedStyle(menu).display : 'none',
                            ariaExpanded: trigger ? trigger.getAttribute('aria-expanded') : 'false'
                        };
                    }
                """)
                print(f"点击前状态: {before_state}")
                
                # 点击菜单
                page.click("#userDropdown")
                time.sleep(1)
                
                # 点击后状态
                after_state = page.evaluate("""
                    () => {
                        const trigger = document.getElementById('userDropdown');
                        const menu = trigger ? trigger.nextElementSibling : null;
                        
                        return {
                            triggerExists: !!trigger,
                            menuExists: !!menu,
                            menuHasShow: menu ? menu.classList.contains('show') : false,
                            menuDisplay: menu ? window.getComputedStyle(menu).display : 'none',
                            ariaExpanded: trigger ? trigger.getAttribute('aria-expanded') : 'false',
                            menuRect: menu ? {
                                width: menu.getBoundingClientRect().width,
                                height: menu.getBoundingClientRect().height,
                                top: menu.getBoundingClientRect().top,
                                left: menu.getBoundingClientRect().left
                            } : null
                        };
                    }
                """)
                print(f"点击后状态: {after_state}")
                
                # 截图
                page.screenshot(path=f"debug_click_{i+1}.png")
                
                # 等待一秒再进行下一次测试
                time.sleep(2)
            
            print("\n📊 测试完成，请查看截图和控制台输出")
            
        except Exception as e:
            print(f"❌ 测试过程中出现错误: {e}")
        
        input("按回车键关闭浏览器...")
        browser.close()

if __name__ == "__main__":
    test_dropdown_simple_debug()
