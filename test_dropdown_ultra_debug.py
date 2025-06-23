#!/usr/bin/env python3
"""
超详细下拉菜单调试脚本
检查事件监听器、DOM结构、JavaScript加载等
"""

import time
import sys
import os
from playwright.sync_api import sync_playwright, expect

def test_dropdown_ultra_debug():
    """超详细调试下拉菜单问题"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=800)
        context = browser.new_context()
        page = context.new_page()
        
        print("=" * 60)
        print("超详细下拉菜单调试")
        print("=" * 60)
        
        try:
            # 1. 登录系统
            print("\n🔐 执行登录...")
            page.goto("http://127.0.0.1:8000/accounts/login/")
            page.fill("input[name='login']", "project_manager")
            page.fill("input[name='password']", "demo123456")
            page.click("button[type='submit']")
            page.wait_for_url("**/dashboard/")
            print("✅ 登录成功")
            
            # 2. 检查页面加载和JavaScript
            print("\n🔍 检查页面加载状态...")
            page_state = page.evaluate("""
                () => {
                    return {
                        documentReady: document.readyState,
                        domContentLoaded: document.readyState === 'complete',
                        jqueryLoaded: typeof jQuery !== 'undefined',
                        bootstrapLoaded: typeof bootstrap !== 'undefined',
                        dropdownFixLoaded: !!document.getElementById('dropdown-fix-css')
                    };
                }
            """)
            print(f"页面状态: {page_state}")
            
            # 3. 检查下拉菜单DOM结构
            print("\n🔍 检查下拉菜单DOM结构...")
            dom_info = page.evaluate("""
                () => {
                    const userDropdown = document.getElementById('userDropdown');
                    const menu = userDropdown ? userDropdown.nextElementSibling : null;
                    
                    return {
                        triggerExists: !!userDropdown,
                        triggerTagName: userDropdown ? userDropdown.tagName : null,
                        triggerClasses: userDropdown ? userDropdown.className : null,
                        triggerId: userDropdown ? userDropdown.id : null,
                        menuExists: !!menu,
                        menuTagName: menu ? menu.tagName : null,
                        menuClasses: menu ? menu.className : null,
                        menuItemsCount: menu ? menu.querySelectorAll('.dropdown-item').length : 0,
                        hasDataBsToggle: userDropdown ? userDropdown.hasAttribute('data-bs-toggle') : false,
                        dataBsToggleValue: userDropdown ? userDropdown.getAttribute('data-bs-toggle') : null
                    };
                }
            """)
            print(f"DOM信息: {dom_info}")
            
            # 4. 检查事件监听器
            print("\n🔍 检查事件监听器...")
            event_info = page.evaluate("""
                () => {
                    const userDropdown = document.getElementById('userDropdown');
                    if (!userDropdown) return { error: 'Trigger not found' };
                    
                    // 检查事件监听器（这个方法不完全可靠，但可以尝试）
                    let hasClickListener = false;
                    try {
                        // 创建一个点击事件来测试
                        const event = new MouseEvent('click', {
                            bubbles: true,
                            cancelable: true,
                            view: window
                        });
                        
                        // 检查是否有事件监听器响应
                        hasClickListener = true; // 我们假设有，因为很难直接检测
                    } catch (e) {
                        hasClickListener = false;
                    }
                    
                    return {
                        triggerFound: true,
                        assumeHasClickListener: hasClickListener,
                        triggerHTML: userDropdown.outerHTML.substring(0, 200) + '...'
                    };
                }
            """)
            print(f"事件信息: {event_info}")
            
            # 5. 检查控制台错误
            print("\n🔍 监听控制台消息...")
            console_messages = []
            
            def handle_console(msg):
                console_messages.append(f"{msg.type}: {msg.text}")
                print(f"控制台 {msg.type}: {msg.text}")
            
            page.on("console", handle_console)
            
            # 6. 手动触发点击事件
            print("\n🔍 手动触发点击事件...")
            click_result = page.evaluate("""
                () => {
                    console.log('开始手动触发点击事件');
                    const userDropdown = document.getElementById('userDropdown');
                    if (!userDropdown) {
                        console.log('错误: 未找到userDropdown元素');
                        return { success: false, error: 'Trigger not found' };
                    }
                    
                    console.log('找到userDropdown元素:', userDropdown);
                    
                    // 创建点击事件
                    const event = new MouseEvent('click', {
                        bubbles: true,
                        cancelable: true,
                        view: window
                    });
                    
                    console.log('创建点击事件:', event);
                    
                    // 触发事件
                    const result = userDropdown.dispatchEvent(event);
                    console.log('点击事件已触发，结果:', result);
                    
                    // 检查菜单状态
                    const menu = userDropdown.nextElementSibling;
                    const menuState = {
                        menuFound: !!menu,
                        hasShowClass: menu ? menu.classList.contains('show') : false,
                        displayStyle: menu ? window.getComputedStyle(menu).display : 'none'
                    };
                    
                    console.log('菜单状态:', menuState);
                    
                    return {
                        success: true,
                        eventDispatched: result,
                        menuState: menuState
                    };
                }
            """)
            print(f"手动点击结果: {click_result}")
            
            # 7. 等待一段时间查看控制台消息
            time.sleep(2)
            
            # 8. 尝试真实的页面点击
            print("\n🔍 尝试真实的页面点击...")
            try:
                page.click("#userDropdown", timeout=3000)
                time.sleep(1)
                
                # 检查点击后的状态
                after_click_state = page.evaluate("""
                    () => {
                        const userDropdown = document.getElementById('userDropdown');
                        const menu = userDropdown ? userDropdown.nextElementSibling : null;
                        
                        return {
                            menuExists: !!menu,
                            hasShowClass: menu ? menu.classList.contains('show') : false,
                            displayStyle: menu ? window.getComputedStyle(menu).display : 'none',
                            ariaExpanded: userDropdown ? userDropdown.getAttribute('aria-expanded') : null
                        };
                    }
                """)
                print(f"真实点击后状态: {after_click_state}")
                
            except Exception as e:
                print(f"真实点击失败: {e}")
            
            # 9. 显示所有控制台消息
            print(f"\n📝 总共收到 {len(console_messages)} 条控制台消息")
            for msg in console_messages:
                print(f"  {msg}")
            
        except Exception as e:
            print(f"❌ 测试过程中出现错误: {e}")
        
        input("按回车键关闭浏览器...")
        browser.close()

if __name__ == "__main__":
    test_dropdown_ultra_debug()
