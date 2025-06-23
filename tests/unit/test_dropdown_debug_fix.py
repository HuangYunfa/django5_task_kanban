#!/usr/bin/env python3
"""
详细的下拉菜单调试与修复脚本
逐步分析和修复下拉菜单显示问题
"""

import time
import sys
import os
from playwright.sync_api import sync_playwright, expect

def dropdown_debug_and_fix():
    """详细的下拉菜单调试与修复"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context()
        page = context.new_page()
        
        print("=" * 70)
        print("下拉菜单详细调试与修复")
        print("=" * 70)
        
        try:
            # 1. 登录
            login(page)
            
            # 2. 检查Bootstrap版本
            check_bootstrap_version(page)
            
            # 3. 检查菜单HTML结构
            check_menu_structure(page)
            
            # 4. 检查菜单CSS样式
            check_menu_css(page)
            
            # 5. 检查菜单JavaScript事件
            check_menu_js_events(page)
            
            # 6. 尝试修复方案1: 纯CSS修复
            attempt_css_fix(page)
            
            # 7. 尝试修复方案2: JavaScript修复
            attempt_js_fix(page)
            
            # 8. 记录修复前后对比
            document_fixes(page)
            
            # 9. 最终验证
            final_verification(page)
            
        except Exception as e:
            print(f"❌ 调试过程中出现错误: {e}")
        
        input("按回车键关闭浏览器...")
        browser.close()

def login(page):
    """执行登录"""
    try:
        print("\n🔐 执行登录...")
        page.goto("http://127.0.0.1:8000/accounts/login/")
        page.fill("input[name='login']", "project_manager")
        page.fill("input[name='password']", "demo123456")
        page.click("button[type='submit']")
        page.wait_for_url("**/dashboard/")
        print("✅ 登录成功")
    except Exception as e:
        print(f"❌ 登录失败: {e}")
        sys.exit(1)

def check_bootstrap_version(page):
    """检查Bootstrap版本"""
    print("\n🔍 检查Bootstrap版本...")
    
    bootstrap_version = page.evaluate("""
        () => {
            // 检查bootstrap对象
            if (typeof bootstrap !== 'undefined') {
                return {
                    exists: true,
                    version: bootstrap.Dropdown ? bootstrap.Dropdown.VERSION || 'unknown' : 'unknown'
                };
            }
            
            // 检查jQuery引导的Bootstrap
            if (typeof $ !== 'undefined' && typeof $.fn !== 'undefined' && typeof $.fn.dropdown !== 'undefined') {
                return {
                    exists: true,
                    version: 'jQuery Bootstrap',
                    jQueryVersion: $.fn.jquery || 'unknown'
                };
            }
            
            // 检查Bootstrap CSS
            const bootstrapCSS = document.querySelector('link[href*="bootstrap"]');
            return {
                exists: false,
                cssExists: !!bootstrapCSS,
                cssHref: bootstrapCSS ? bootstrapCSS.href : null
            };
        }
    """)
    
    print(f"   📊 Bootstrap信息: {bootstrap_version}")

def check_menu_structure(page):
    """检查菜单HTML结构"""
    print("\n🔍 检查菜单HTML结构...")
    
    # 1. 检查用户下拉菜单结构
    user_dropdown_structure = page.evaluate("""
        () => {
            const userDropdown = document.getElementById('userDropdown');
            if (!userDropdown) return { exists: false };
            
            const userMenu = userDropdown.nextElementSibling;
            if (!userMenu) return { triggerExists: true, menuExists: false };
            
            const items = Array.from(userMenu.querySelectorAll('.dropdown-item')).map(item => ({
                text: item.innerText.trim(),
                href: item.getAttribute('href'),
                hasClasses: item.className
            }));
            
            return {
                triggerExists: true,
                menuExists: true,
                menuId: userMenu.id || null,
                menuClasses: userMenu.className,
                menuHasShowClass: userMenu.classList.contains('show'),
                itemCount: items.length,
                items: items
            };
        }
    """)
    
    print(f"   📊 用户下拉菜单结构: {user_dropdown_structure}")
    
    # 2. 检查API下拉菜单结构
    api_dropdown_structure = page.evaluate("""
        () => {
            const apiDropdown = document.getElementById('apiDropdown');
            if (!apiDropdown) return { exists: false };
            
            const apiMenu = apiDropdown.nextElementSibling;
            if (!apiMenu) return { triggerExists: true, menuExists: false };
            
            const items = Array.from(apiMenu.querySelectorAll('.dropdown-item')).map(item => ({
                text: item.innerText.trim(),
                href: item.getAttribute('href'),
                hasClasses: item.className
            }));
            
            return {
                triggerExists: true,
                menuExists: true,
                menuId: apiMenu.id || null,
                menuClasses: apiMenu.className,
                menuHasShowClass: apiMenu.classList.contains('show'),
                itemCount: items.length,
                items: items
            };
        }
    """)
    
    print(f"   📊 API下拉菜单结构: {api_dropdown_structure}")
    
    # 3. 检查菜单标签结构
    menu_tags = page.evaluate("""
        () => {
            const userDropdown = document.getElementById('userDropdown');
            if (!userDropdown) return { userTriggerTag: 'not found' };
            
            const userMenu = userDropdown.nextElementSibling;
            
            return {
                userTriggerTag: userDropdown.tagName,
                userTriggerAttributes: {
                    'data-bs-toggle': userDropdown.getAttribute('data-bs-toggle'),
                    'aria-expanded': userDropdown.getAttribute('aria-expanded'),
                    'href': userDropdown.getAttribute('href')
                },
                userMenuTag: userMenu ? userMenu.tagName : 'not found',
                userMenuAttributes: userMenu ? {
                    'aria-labelledby': userMenu.getAttribute('aria-labelledby')
                } : {}
            };
        }
    """)
    
    print(f"   📊 菜单标签结构: {menu_tags}")

def check_menu_css(page):
    """检查菜单CSS样式"""
    print("\n🔍 检查菜单CSS样式...")
    
    # 1. 获取用户下拉菜单计算样式
    user_menu_css = page.evaluate("""
        () => {
            const userDropdown = document.getElementById('userDropdown');
            if (!userDropdown) return { exists: false };
            
            const userMenu = userDropdown.nextElementSibling;
            if (!userMenu) return { triggerExists: true, menuExists: false };
            
            const menuStyle = window.getComputedStyle(userMenu);
            
            return {
                display: menuStyle.display,
                visibility: menuStyle.visibility,
                opacity: menuStyle.opacity,
                position: menuStyle.position,
                zIndex: menuStyle.zIndex,
                transform: menuStyle.transform,
                maxHeight: menuStyle.maxHeight,
                overflow: menuStyle.overflow,
                
                // 重要样式对比
                hasDisplayNone: menuStyle.display === 'none',
                hasVisibilityHidden: menuStyle.visibility === 'hidden',
                hasZeroOpacity: parseFloat(menuStyle.opacity) === 0,
                hasTransform: menuStyle.transform !== 'none'
            };
        }
    """)
    
    print(f"   📊 用户下拉菜单样式: {user_menu_css}")
    
    # 2. 获取菜单项样式
    menu_item_css = page.evaluate("""
        () => {
            const userDropdown = document.getElementById('userDropdown');
            if (!userDropdown) return { exists: false };
            
            const userMenu = userDropdown.nextElementSibling;
            if (!userMenu) return { triggerExists: true, menuExists: false };
            
            const firstItem = userMenu.querySelector('.dropdown-item');
            if (!firstItem) return { menuExists: true, itemExists: false };
            
            const itemStyle = window.getComputedStyle(firstItem);
            
            return {
                display: itemStyle.display,
                visibility: itemStyle.visibility,
                opacity: itemStyle.opacity,
                padding: itemStyle.padding,
                lineHeight: itemStyle.lineHeight
            };
        }
    """)
    
    print(f"   📊 菜单项样式: {menu_item_css}")
    
    # 3. 检查父元素是否影响菜单
    parent_impact = page.evaluate("""
        () => {
            const userDropdown = document.getElementById('userDropdown');
            if (!userDropdown) return { exists: false };
            
            const userMenu = userDropdown.nextElementSibling;
            if (!userMenu) return { triggerExists: true, menuExists: false };
            
            const parent = userDropdown.parentElement;
            const parentStyle = window.getComputedStyle(parent);
            
            return {
                parentTag: parent.tagName,
                parentClasses: parent.className,
                parentPosition: parentStyle.position,
                parentOverflow: parentStyle.overflow
            };
        }
    """)
    
    print(f"   📊 父元素影响: {parent_impact}")

def check_menu_js_events(page):
    """检查菜单JavaScript事件"""
    print("\n🔍 检查菜单JavaScript事件...")
    
    # 1. 检查点击事件是否正确绑定
    click_events = page.evaluate("""
        () => {
            // 检查是否直接使用了Bootstrap初始化
            let hasBootstrapInit = false;
            let hasJQueryInit = false;
            
            // 检查页面脚本
            const scripts = Array.from(document.querySelectorAll('script')).map(s => s.src);
            const inlineScripts = Array.from(document.querySelectorAll('script:not([src])')).map(s => s.textContent);
            
            // 查找可能的初始化代码
            const dropdownInitPattern = /dropdown|toggle/i;
            const hasDropdownInit = inlineScripts.some(script => dropdownInitPattern.test(script));
            
            return {
                hasBootstrapInit,
                hasJQueryInit,
                scripts,
                hasDropdownInit
            };
        }
    """)
    
    print(f"   📊 点击事件信息: {click_events}")
    
    # 2. 手动触发点击事件并监控变化
    try:
        print("\n   🖱️ 手动点击用户下拉菜单触发器...")
        
        # 获取点击前状态
        before_click = page.evaluate("""
            () => {
                const userDropdown = document.getElementById('userDropdown');
                const userMenu = userDropdown ? userDropdown.nextElementSibling : null;
                return {
                    menuDisplay: userMenu ? window.getComputedStyle(userMenu).display : 'unknown',
                    menuHasShowClass: userMenu ? userMenu.classList.contains('show') : false,
                    triggerAriaExpanded: userDropdown ? userDropdown.getAttribute('aria-expanded') : null
                };
            }
        """)
        
        print(f"      点击前: {before_click}")
        
        # 执行点击
        page.click("#userDropdown")
        time.sleep(0.5)
        
        # 获取点击后状态
        after_click = page.evaluate("""
            () => {
                const userDropdown = document.getElementById('userDropdown');
                const userMenu = userDropdown ? userDropdown.nextElementSibling : null;
                return {
                    menuDisplay: userMenu ? window.getComputedStyle(userMenu).display : 'unknown',
                    menuHasShowClass: userMenu ? userMenu.classList.contains('show') : false,
                    triggerAriaExpanded: userDropdown ? userDropdown.getAttribute('aria-expanded') : null,
                    
                    // 详细检查
                    menuComputedStyles: userMenu ? {
                        display: window.getComputedStyle(userMenu).display,
                        visibility: window.getComputedStyle(userMenu).visibility,
                        opacity: window.getComputedStyle(userMenu).opacity,
                        transform: window.getComputedStyle(userMenu).transform
                    } : {}
                };
            }
        """)
        
        print(f"      点击后: {after_click}")
        
        # 再点击一次（应该关闭菜单）
        page.click("#userDropdown")
        time.sleep(0.5)
        
        # 获取再次点击后状态
        after_second_click = page.evaluate("""
            () => {
                const userDropdown = document.getElementById('userDropdown');
                const userMenu = userDropdown ? userDropdown.nextElementSibling : null;
                return {
                    menuDisplay: userMenu ? window.getComputedStyle(userMenu).display : 'unknown',
                    menuHasShowClass: userMenu ? userMenu.classList.contains('show') : false,
                    triggerAriaExpanded: userDropdown ? userDropdown.getAttribute('aria-expanded') : null
                };
            }
        """)
        
        print(f"      再次点击后: {after_second_click}")
    
    except Exception as e:
        print(f"      ❌ 点击测试出错: {e}")

def attempt_css_fix(page):
    """尝试CSS修复方案"""
    print("\n🛠️ 尝试CSS修复方案...")
    
    # 创建CSS修复代码
    css_fix = page.evaluate("""
        () => {
            // 1. 创建一个新的style元素
            const style = document.createElement('style');
            style.id = 'dropdown-fix-css';
            style.textContent = `
                /* 修复下拉菜单不显示的问题 */
                .dropdown-menu.show {
                    display: block !important;
                    visibility: visible !important;
                    opacity: 1 !important;
                    transform: none !important;
                    height: auto !important;
                    overflow: visible !important;
                    max-height: none !important;
                    min-height: auto !important;
                    pointer-events: auto !important;
                }
                
                /* 修复下拉菜单项不显示的问题 */
                .dropdown-menu.show .dropdown-item {
                    display: block !important;
                    visibility: visible !important;
                    opacity: 1 !important;
                }
                
                /* 尝试修复父容器可能引起的问题 */
                .dropdown {
                    position: relative !important;
                    overflow: visible !important;
                }
                
                /* 确保用户下拉菜单在最上层 */
                #userDropdown + .dropdown-menu.show,
                #apiDropdown + .dropdown-menu.show,
                #notificationDropdown + .dropdown-menu.show {
                    z-index: 9999 !important;
                    position: absolute !important;
                }
            `;
            
            // 2. 添加到文档头部
            document.head.appendChild(style);
            
            // 3. 返回结果
            return {
                fixApplied: true,
                styleId: style.id,
                cssRules: style.textContent
            };
        }
    """)
    
    print(f"   📊 CSS修复应用结果: {css_fix}")
    
    # 测试修复效果
    print("\n   🧪 测试CSS修复效果...")
    test_dropdown_after_fix(page)

def attempt_js_fix(page):
    """尝试JavaScript修复方案"""
    print("\n🛠️ 尝试JavaScript修复方案...")
    
    # 创建JS修复代码
    js_fix = page.evaluate("""
        () => {
            // 1. 定义全局处理函数
            window.fixDropdowns = function() {
                // 处理所有带有data-bs-toggle="dropdown"的元素
                document.querySelectorAll('[data-bs-toggle="dropdown"]').forEach(trigger => {
                    // 如果已经有事件监听器，先移除
                    trigger.removeEventListener('click', handleDropdownClick);
                    // 添加新的事件监听器
                    trigger.addEventListener('click', handleDropdownClick);
                });
                
                console.log('已修复下拉菜单点击事件');
            };
            
            // 2. 定义点击处理函数
            function handleDropdownClick(event) {
                event.preventDefault();
                event.stopPropagation();
                
                // 获取对应的菜单元素
                const menu = this.nextElementSibling;
                if (!menu || !menu.classList.contains('dropdown-menu')) return;
                
                // 切换show类
                menu.classList.toggle('show');
                
                // 更新aria-expanded属性
                this.setAttribute('aria-expanded', menu.classList.contains('show') ? 'true' : 'false');
                
                // 如果显示了菜单，点击其他区域时隐藏
                if (menu.classList.contains('show')) {
                    const closeOnClickOutside = (e) => {
                        if (!menu.contains(e.target) && e.target !== this) {
                            menu.classList.remove('show');
                            this.setAttribute('aria-expanded', 'false');
                            document.removeEventListener('click', closeOnClickOutside);
                        }
                    };
                    
                    // 延迟添加事件监听器，避免当前点击立即触发
                    setTimeout(() => {
                        document.addEventListener('click', closeOnClickOutside);
                    }, 0);
                }
                
                console.log('下拉菜单状态切换:', menu.classList.contains('show'));
            }
            
            // 3. 立即执行修复
            window.fixDropdowns();
            
            // 4. 返回结果
            return {
                fixApplied: true,
                handlerName: 'fixDropdowns',
                targets: {
                    userDropdown: !!document.getElementById('userDropdown'),
                    apiDropdown: !!document.getElementById('apiDropdown'),
                    notificationDropdown: !!document.getElementById('notificationDropdown')
                }
            };
        }
    """)
    
    print(f"   📊 JavaScript修复应用结果: {js_fix}")
    
    # 测试修复效果
    print("\n   🧪 测试JavaScript修复效果...")
    test_dropdown_after_fix(page)

def test_dropdown_after_fix(page):
    """测试修复后的下拉菜单"""
    try:
        # 点击用户下拉菜单
        page.click("#userDropdown")
        time.sleep(0.5)
        
        # 检查菜单状态
        user_menu_status = page.evaluate("""
            () => {
                const userDropdown = document.getElementById('userDropdown');
                const userMenu = userDropdown ? userDropdown.nextElementSibling : null;
                if (!userMenu) return { menuExists: false };
                
                const menuStyle = window.getComputedStyle(userMenu);
                const firstItem = userMenu.querySelector('.dropdown-item');
                const firstItemStyle = firstItem ? window.getComputedStyle(firstItem) : null;
                
                return {
                    menuExists: true,
                    hasShowClass: userMenu.classList.contains('show'),
                    display: menuStyle.display,
                    visibility: menuStyle.visibility,
                    opacity: menuStyle.opacity,
                    firstItemVisible: firstItem ? firstItemStyle.display !== 'none' : false
                };
            }
        """)
        
        print(f"      📊 用户菜单状态: {user_menu_status}")
        
        # 检查菜单项是否可见
        menu_items_visible = page.evaluate("""
            () => {
                const userMenu = document.querySelector('#userDropdown + .dropdown-menu');
                if (!userMenu) return { visible: false };
                
                const items = userMenu.querySelectorAll('.dropdown-item');
                const visibleItems = Array.from(items).filter(item => {
                    const style = window.getComputedStyle(item);
                    return style.display !== 'none' && style.visibility !== 'hidden';
                });
                
                return {
                    totalItems: items.length,
                    visibleItems: visibleItems.length,
                    allVisible: visibleItems.length === items.length,
                    itemTexts: Array.from(items).map(item => item.innerText.trim())
                };
            }
        """)
        
        print(f"      📊 菜单项可见性: {menu_items_visible}")
        
        # 再次点击关闭菜单
        page.click("#userDropdown")
        
        # 测试API下拉菜单
        print("\n      🧪 测试API下拉菜单...")
        page.click("#apiDropdown")
        time.sleep(0.5)
        
        api_menu_status = page.evaluate("""
            () => {
                const apiDropdown = document.getElementById('apiDropdown');
                const apiMenu = apiDropdown ? apiDropdown.nextElementSibling : null;
                if (!apiMenu) return { menuExists: false };
                
                const menuStyle = window.getComputedStyle(apiMenu);
                
                return {
                    menuExists: true,
                    hasShowClass: apiMenu.classList.contains('show'),
                    display: menuStyle.display,
                    visibility: menuStyle.visibility,
                    opacity: menuStyle.opacity
                };
            }
        """)
        
        print(f"      📊 API菜单状态: {api_menu_status}")
        
    except Exception as e:
        print(f"      ❌ 测试修复效果出错: {e}")

def document_fixes(page):
    """记录修复前后对比"""
    print("\n📝 记录修复前后对比...")
    
    # 定义和记录修复方案
    fixes = [
        {
            "问题": "下拉菜单不显示或显示为滚动条",
            "原因": "Bootstrap下拉菜单初始化问题，菜单元素的display属性没有正确设置为block",
            "修复方案": [
                "1. 通过CSS强制设置.dropdown-menu.show为display:block",
                "2. 手动实现下拉菜单的JavaScript点击事件处理",
                "3. 确保所有菜单项可见性"
            ]
        }
    ]
    
    for i, fix in enumerate(fixes, 1):
        print(f"\n   🔧 修复 {i}: {fix['问题']}")
        print(f"      原因: {fix['原因']}")
        print("      修复方案:")
        for step in fix['修复方案']:
            print(f"      - {step}")

def final_verification(page):
    """最终验证修复效果"""
    print("\n🧪 最终验证修复效果...")
    
    # 创建一个最终修复脚本，组合CSS和JS的修复方案
    final_fix = page.evaluate("""
        () => {
            // 1. 确保CSS修复已应用
            if (!document.getElementById('dropdown-fix-css')) {
                const style = document.createElement('style');
                style.id = 'dropdown-fix-css';
                style.textContent = `
                    /* 修复下拉菜单不显示的问题 */
                    .dropdown-menu.show {
                        display: block !important;
                        visibility: visible !important;
                        opacity: 1 !important;
                        transform: none !important;
                        height: auto !important;
                        overflow: visible !important;
                        max-height: none !important;
                        min-height: auto !important;
                        pointer-events: auto !important;
                    }
                    
                    /* 修复下拉菜单项不显示的问题 */
                    .dropdown-menu.show .dropdown-item {
                        display: block !important;
                        visibility: visible !important;
                        opacity: 1 !important;
                    }
                    
                    /* 尝试修复父容器可能引起的问题 */
                    .dropdown {
                        position: relative !important;
                        overflow: visible !important;
                    }
                    
                    /* 确保用户下拉菜单在最上层 */
                    #userDropdown + .dropdown-menu.show,
                    #apiDropdown + .dropdown-menu.show,
                    #notificationDropdown + .dropdown-menu.show {
                        z-index: 9999 !important;
                        position: absolute !important;
                    }
                `;
                document.head.appendChild(style);
            }
            
            // 2. 创建一个全局函数来替换Bootstrap的下拉菜单处理
            window.fixAllDropdowns = function() {
                // 处理所有带有data-bs-toggle="dropdown"的元素
                document.querySelectorAll('[data-bs-toggle="dropdown"]').forEach(trigger => {
                    // 如果已经有事件监听器，先移除
                    trigger.removeEventListener('click', handleDropdownClick);
                    // 添加新的事件监听器
                    trigger.addEventListener('click', handleDropdownClick);
                });
                
                console.log('已全局修复下拉菜单点击事件');
            };
            
            // 3. 定义点击处理函数
            function handleDropdownClick(event) {
                event.preventDefault();
                event.stopPropagation();
                
                // 获取对应的菜单元素
                const menu = this.nextElementSibling;
                if (!menu || !menu.classList.contains('dropdown-menu')) return;
                
                // 首先关闭所有其他菜单
                document.querySelectorAll('.dropdown-menu.show').forEach(openMenu => {
                    if (openMenu !== menu) {
                        openMenu.classList.remove('show');
                        const trigger = openMenu.previousElementSibling;
                        if (trigger) trigger.setAttribute('aria-expanded', 'false');
                    }
                });
                
                // 切换show类
                menu.classList.toggle('show');
                
                // 更新aria-expanded属性
                this.setAttribute('aria-expanded', menu.classList.contains('show') ? 'true' : 'false');
                
                // 强制应用样式
                if (menu.classList.contains('show')) {
                    menu.style.display = 'block';
                    menu.style.visibility = 'visible';
                    menu.style.opacity = '1';
                    
                    // 确保所有菜单项可见
                    menu.querySelectorAll('.dropdown-item').forEach(item => {
                        item.style.display = 'block';
                        item.style.visibility = 'visible';
                        item.style.opacity = '1';
                    });
                    
                    // 点击其他区域时隐藏
                    const closeOnClickOutside = (e) => {
                        if (!menu.contains(e.target) && e.target !== this) {
                            menu.classList.remove('show');
                            menu.style.display = 'none';
                            this.setAttribute('aria-expanded', 'false');
                            document.removeEventListener('click', closeOnClickOutside);
                        }
                    };
                    
                    // 延迟添加事件监听器，避免当前点击立即触发
                    setTimeout(() => {
                        document.addEventListener('click', closeOnClickOutside);
                    }, 0);
                } else {
                    menu.style.display = 'none';
                }
                
                console.log('下拉菜单状态切换:', menu.classList.contains('show'));
            }
            
            // 4. 立即执行修复
            window.fixAllDropdowns();
            
            // 5. 添加页面加载时执行
            window.addEventListener('DOMContentLoaded', window.fixAllDropdowns);
            
            // 6. 返回结果
            return {
                finalFixApplied: true,
                cssFixApplied: !!document.getElementById('dropdown-fix-css'),
                jsFixFunction: 'fixAllDropdowns',
                targets: {
                    userDropdown: !!document.getElementById('userDropdown'),
                    apiDropdown: !!document.getElementById('apiDropdown'),
                    notificationDropdown: !!document.getElementById('notificationDropdown')
                }
            };
        }
    """)
    
    print(f"   📊 最终修复应用结果: {final_fix}")
    
    # 测试用户下拉菜单
    try:
        print("\n   🧪 最终测试用户下拉菜单...")
        page.click("#userDropdown")
        time.sleep(0.5)
        
        # 检查菜单是否可见
        user_menu_visible = page.evaluate("""
            () => {
                const userMenu = document.querySelector('#userDropdown + .dropdown-menu');
                if (!userMenu) return { visible: false };
                
                const menuStyle = window.getComputedStyle(userMenu);
                
                // 检查菜单项
                const items = userMenu.querySelectorAll('.dropdown-item');
                const visibleItems = Array.from(items).filter(item => {
                    const style = window.getComputedStyle(item);
                    return style.display !== 'none' && style.visibility !== 'hidden';
                });
                
                return {
                    menuVisible: menuStyle.display !== 'none' && menuStyle.visibility !== 'hidden',
                    menuHasShowClass: userMenu.classList.contains('show'),
                    totalItems: items.length,
                    visibleItems: visibleItems.length,
                    allItemsVisible: visibleItems.length === items.length,
                    itemTexts: Array.from(items).map(item => item.innerText.trim())
                };
            }
        """)
        
        print(f"      📊 用户菜单可见性: {user_menu_visible}")
        
        # 尝试使用Playwright API检测可见性
        print("\n      使用Playwright检测菜单可见性...")
        
        user_menu = page.locator("#userDropdown + .dropdown-menu")
        is_visible = user_menu.is_visible()
        print(f"      用户菜单可见 (Playwright): {is_visible}")
        
        if is_visible:
            menu_items = page.locator("#userDropdown + .dropdown-menu .dropdown-item")
            count = menu_items.count()
            print(f"      找到 {count} 个菜单项")
            
            for i in range(count):
                item = menu_items.nth(i)
                text = item.inner_text().strip()
                item_visible = item.is_visible()
                print(f"      菜单项 {i+1}: '{text}' (可见: {item_visible})")
        
        # 再次点击关闭菜单
        page.click("#userDropdown")
        
        # 生成最终的修复脚本
        create_final_fix_script(page)
        
    except Exception as e:
        print(f"      ❌ 最终验证出错: {e}")

def create_final_fix_script(page):
    """生成最终的修复脚本"""
    print("\n📝 生成最终修复脚本...")
    
    # 保存修复脚本到static/js/dropdown-fix.js
    fix_script = """
// 下拉菜单修复脚本
// 修复菜单不显示或显示为滚动条的问题

document.addEventListener('DOMContentLoaded', function() {
    // 1. 添加CSS修复
    const style = document.createElement('style');
    style.id = 'dropdown-fix-css';
    style.textContent = `
        /* 修复下拉菜单不显示的问题 */
        .dropdown-menu.show {
            display: block !important;
            visibility: visible !important;
            opacity: 1 !important;
            transform: none !important;
            height: auto !important;
            overflow: visible !important;
            max-height: none !important;
            min-height: auto !important;
            pointer-events: auto !important;
        }
        
        /* 修复下拉菜单项不显示的问题 */
        .dropdown-menu.show .dropdown-item {
            display: block !important;
            visibility: visible !important;
            opacity: 1 !important;
        }
        
        /* 尝试修复父容器可能引起的问题 */
        .dropdown {
            position: relative !important;
            overflow: visible !important;
        }
        
        /* 确保用户下拉菜单在最上层 */
        #userDropdown + .dropdown-menu.show,
        #apiDropdown + .dropdown-menu.show,
        #notificationDropdown + .dropdown-menu.show {
            z-index: 9999 !important;
            position: absolute !important;
        }
    `;
    document.head.appendChild(style);
    
    // 2. 修复下拉菜单点击事件
    function fixAllDropdowns() {
        // 处理所有带有data-bs-toggle="dropdown"的元素
        document.querySelectorAll('[data-bs-toggle="dropdown"]').forEach(trigger => {
            // 如果已经有事件监听器，先移除
            trigger.removeEventListener('click', handleDropdownClick);
            // 添加新的事件监听器
            trigger.addEventListener('click', handleDropdownClick);
        });
        
        console.log('已全局修复下拉菜单点击事件');
    }
    
    // 3. 定义点击处理函数
    function handleDropdownClick(event) {
        event.preventDefault();
        event.stopPropagation();
        
        // 获取对应的菜单元素
        const menu = this.nextElementSibling;
        if (!menu || !menu.classList.contains('dropdown-menu')) return;
        
        // 首先关闭所有其他菜单
        document.querySelectorAll('.dropdown-menu.show').forEach(openMenu => {
            if (openMenu !== menu) {
                openMenu.classList.remove('show');
                const trigger = openMenu.previousElementSibling;
                if (trigger) trigger.setAttribute('aria-expanded', 'false');
            }
        });
        
        // 切换show类
        menu.classList.toggle('show');
        
        // 更新aria-expanded属性
        this.setAttribute('aria-expanded', menu.classList.contains('show') ? 'true' : 'false');
        
        // 强制应用样式
        if (menu.classList.contains('show')) {
            menu.style.display = 'block';
            menu.style.visibility = 'visible';
            menu.style.opacity = '1';
            
            // 确保所有菜单项可见
            menu.querySelectorAll('.dropdown-item').forEach(item => {
                item.style.display = 'block';
                item.style.visibility = 'visible';
                item.style.opacity = '1';
            });
            
            // 点击其他区域时隐藏
            const closeOnClickOutside = (e) => {
                if (!menu.contains(e.target) && e.target !== this) {
                    menu.classList.remove('show');
                    menu.style.display = 'none';
                    this.setAttribute('aria-expanded', 'false');
                    document.removeEventListener('click', closeOnClickOutside);
                }
            };
            
            // 延迟添加事件监听器，避免当前点击立即触发
            setTimeout(() => {
                document.addEventListener('click', closeOnClickOutside);
            }, 0);
        } else {
            menu.style.display = 'none';
        }
        
        console.log('下拉菜单状态切换:', menu.classList.contains('show'));
    }
    
    // 立即执行修复
    fixAllDropdowns();
    
    // 确保在DOM变化时重新应用修复
    const observer = new MutationObserver(function(mutations) {
        fixAllDropdowns();
    });
    
    observer.observe(document.body, { 
        childList: true, 
        subtree: true 
    });
});
"""
    
    print("   ✅ 修复脚本生成完成")
    print("   🔧 请将此脚本保存到taskkanban/static/js/dropdown-fix.js并在base.html中引用")
    
    # 生成HTML引用代码
    html_include = """
<!-- 引入下拉菜单修复脚本 -->
<script src="{% static 'js/dropdown-fix.js' %}"></script>
"""
    
    print("\n   HTML引用代码:")
    print(html_include)
    
    # 添加应用CSS的方法
    inline_css = """
<style id="dropdown-fix-css">
    /* 修复下拉菜单不显示的问题 */
    .dropdown-menu.show {
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
        transform: none !important;
        height: auto !important;
        overflow: visible !important;
        max-height: none !important;
        min-height: auto !important;
        pointer-events: auto !important;
    }
    
    /* 修复下拉菜单项不显示的问题 */
    .dropdown-menu.show .dropdown-item {
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
    }
    
    /* 尝试修复父容器可能引起的问题 */
    .dropdown {
        position: relative !important;
        overflow: visible !important;
    }
    
    /* 确保用户下拉菜单在最上层 */
    #userDropdown + .dropdown-menu.show,
    #apiDropdown + .dropdown-menu.show,
    #notificationDropdown + .dropdown-menu.show {
        z-index: 9999 !important;
        position: absolute !important;
    }
</style>
"""
    
    print("\n   或者直接在head中添加内联CSS:")
    print(inline_css)

if __name__ == "__main__":
    dropdown_debug_and_fix()
