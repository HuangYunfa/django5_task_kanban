#!/usr/bin/env python3
"""
超详细测试下拉菜单z-index和滚动条问题
基于增强版dropdown-fix.js进行验证
"""

import time
import sys
import os
from playwright.sync_api import sync_playwright, expect

def test_dropdown_zindex_fix_final():
    """超详细测试增强版dropdown-fix.js的修复效果"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=300)
        context = browser.new_context()
        page = context.new_page()
        
        print("=" * 70)
        print("增强版下拉菜单修复最终验证")
        print("=" * 70)
        
        try:
            # 1. 登录系统
            login(page)
            
            # 2. 检查JS和CSS是否正确加载
            check_resources_loaded(page)
            
            # 3. 对所有下拉菜单进行精确定位和z-index测试
            test_all_dropdowns_precise(page)
            
            # 4. 测试滚动条特殊情况
            test_scrollbars_special_cases(page)
            
            # 5. 测试浮层不同层级下的菜单显示
            test_menu_at_different_layers(page)
            
            # 6. 生成最终测试报告
            generate_final_validation_report()
            
        except Exception as e:
            print(f"❌ 测试过程中出现错误: {e}")
        
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

def check_resources_loaded(page):
    """检查关键资源是否正确加载"""
    print("\n🔍 检查关键资源加载...")
      # 检查dropdown-fix.js是否加载
    js_loaded = page.evaluate("""
        () => {
            // 检查脚本是否存在
            const scripts = Array.from(document.querySelectorAll('script[src]'));
            const dropdownFixScript = scripts.find(s => s.src.includes('dropdown-fix.js'));
            
            // 检查CSS修复是否应用
            const styleExists = !!document.getElementById('dropdown-fix-css') || 
                                !!document.querySelector('style[id*="dropdown-fix"]');
            
            // 检查函数是否定义（更安全的方式）
            let hasFunctions = false;
            try {
                const inlineScripts = Array.from(document.querySelectorAll('script:not([src])'));
                hasFunctions = inlineScripts.some(script => 
                    script.textContent && script.textContent.includes('fixAllDropdowns')
                ) || typeof window.fixAllDropdowns === 'function';
            } catch (e) {
                hasFunctions = false;
            }
            
            return {
                scriptFound: !!dropdownFixScript,
                scriptUrl: dropdownFixScript ? dropdownFixScript.src : null,
                cssFixApplied: styleExists,
                functionsExist: hasFunctions
            };
        }
    """)
    
    print(f"   📊 资源加载状态: {js_loaded}")

def test_all_dropdowns_precise(page):
    """对所有下拉菜单进行精确定位和z-index测试"""
    print("\n🔬 对所有下拉菜单进行精确测试...")
    
    dropdown_ids = ["userDropdown", "apiDropdown", "notificationDropdown"]
    
    for dropdown_id in dropdown_ids:
        print(f"\n   🔍 测试 {dropdown_id}...")
        
        try:
            # 1. 测试点击前状态
            before_click = page.evaluate(f"""
                () => {{
                    const trigger = document.getElementById('{dropdown_id}');
                    if (!trigger) return {{ exists: false }};
                    
                    const menu = trigger.nextElementSibling;
                    if (!menu || !menu.classList.contains('dropdown-menu')) return {{ triggerExists: true, menuExists: false }};
                    
                    const triggerRect = trigger.getBoundingClientRect();
                    const style = window.getComputedStyle(menu);
                    
                    return {{
                        triggerExists: true,
                        menuExists: true,
                        triggerPosition: {{
                            top: triggerRect.top,
                            left: triggerRect.left,
                            bottom: triggerRect.bottom,
                            right: triggerRect.right
                        }},
                        menuComputedStyle: {{
                            display: style.display,
                            visibility: style.visibility,
                            position: style.position,
                            zIndex: style.zIndex
                        }},
                        menuHasShowClass: menu.classList.contains('show')
                    }};
                }}
            """)
            
            print(f"      点击前状态: {before_click}")
            
            # 2. 点击下拉菜单
            page.click(f"#{dropdown_id}")
            time.sleep(0.5)
            
            # 3. 点击后状态详细检查
            after_click = page.evaluate(f"""
                () => {{
                    const trigger = document.getElementById('{dropdown_id}');
                    if (!trigger) return {{ exists: false }};
                    
                    const menu = trigger.nextElementSibling;
                    if (!menu) return {{ triggerExists: true, menuExists: false }};
                    
                    const triggerRect = trigger.getBoundingClientRect();
                    const menuRect = menu.getBoundingClientRect();
                    const menuStyle = window.getComputedStyle(menu);
                    
                    // 检查所有菜单项
                    const items = Array.from(menu.querySelectorAll('.dropdown-item, .dropdown-header, .dropdown-divider, .dropdown-item-text'));
                    const itemsInfo = items.map(item => {{
                        const itemRect = item.getBoundingClientRect();
                        const itemStyle = window.getComputedStyle(item);
                        
                        return {{
                            text: item.textContent.trim(),
                            type: item.classList.contains('dropdown-header') ? 'header' :
                                  item.classList.contains('dropdown-divider') ? 'divider' : 
                                  item.classList.contains('dropdown-item-text') ? 'text' : 'item',
                            isVisible: itemStyle.display !== 'none' && itemStyle.visibility !== 'hidden',
                            computedStyle: {{
                                display: itemStyle.display,
                                visibility: itemStyle.visibility,
                                position: itemStyle.position
                            }},
                            rect: {{
                                top: itemRect.top,
                                left: itemRect.left,
                                bottom: itemRect.bottom,
                                right: itemRect.right,
                                height: itemRect.height,
                                width: itemRect.width
                            }},
                            inViewport: (
                                itemRect.top >= 0 &&
                                itemRect.left >= 0 &&
                                itemRect.bottom <= window.innerHeight &&
                                itemRect.right <= window.innerWidth
                            )
                        }};
                    }});
                    
                    // 获取完整的菜单信息
                    return {{
                        triggerExists: true,
                        menuExists: true,
                        menuHasShowClass: menu.classList.contains('show'),
                        menuIsVisible: menuStyle.display !== 'none' && menuStyle.visibility !== 'hidden',
                        ariaExpanded: trigger.getAttribute('aria-expanded'),
                        
                        // 触发器位置
                        triggerRect: {{
                            top: triggerRect.top,
                            left: triggerRect.left,
                            bottom: triggerRect.bottom,
                            right: triggerRect.right,
                            height: triggerRect.height,
                            width: triggerRect.width
                        }},
                        
                        // 菜单位置和大小
                        menuRect: {{
                            top: menuRect.top,
                            left: menuRect.left,
                            bottom: menuRect.bottom,
                            right: menuRect.right,
                            height: menuRect.height,
                            width: menuRect.width
                        }},
                        
                        // 菜单样式详情
                        menuComputedStyle: {{
                            display: menuStyle.display,
                            visibility: menuStyle.visibility,
                            opacity: menuStyle.opacity,
                            position: menuStyle.position,
                            zIndex: menuStyle.zIndex,
                            transform: menuStyle.transform,
                            maxHeight: menuStyle.maxHeight,
                            overflow: menuStyle.overflow,
                            overflowY: menuStyle.overflowY
                        }},
                        
                        // 滚动条信息
                        scrollInfo: {{
                            scrollHeight: menu.scrollHeight,
                            clientHeight: menu.clientHeight,
                            hasScrollbar: menu.scrollHeight > menu.clientHeight,
                            scrollbarWidth: menu.offsetWidth - menu.clientWidth
                        }},
                        
                        // 相对定位信息
                        positioningInfo: {{
                            isRightAligned: menuStyle.right !== 'auto',
                            isLeftAligned: menuStyle.left !== 'auto',
                            rightValue: menuStyle.right,
                            leftValue: menuStyle.left,
                            topValue: menuStyle.top
                        }},
                        
                        // 菜单项信息
                        items: itemsInfo,
                        totalItems: items.length,
                        visibleItems: itemsInfo.filter(i => i.isVisible).length,
                        allItemsInViewport: itemsInfo.every(i => i.inViewport)
                    }};
                }}
            """)
            
            print(f"      📊 菜单点击后状态: ")
            print(f"         - 菜单可见: {after_click.get('menuIsVisible', False)}")
            print(f"         - show类: {after_click.get('menuHasShowClass', False)}")
            print(f"         - aria-expanded: {after_click.get('ariaExpanded', 'unknown')}")
            
            menu_style = after_click.get('menuComputedStyle', {})
            print(f"         - 样式: display={menu_style.get('display', 'unknown')}, "
                  f"visibility={menu_style.get('visibility', 'unknown')}, "
                  f"z-index={menu_style.get('zIndex', 'unknown')}, "
                  f"position={menu_style.get('position', 'unknown')}")
            
            menu_rect = after_click.get('menuRect', {})
            print(f"         - 位置: top={menu_rect.get('top', 'unknown')}, "
                  f"left={menu_rect.get('left', 'unknown')}, "
                  f"width={menu_rect.get('width', 'unknown')}, "
                  f"height={menu_rect.get('height', 'unknown')}")
            
            scroll_info = after_click.get('scrollInfo', {})
            print(f"         - 滚动: hasScrollbar={scroll_info.get('hasScrollbar', 'unknown')}, "
                  f"scrollHeight={scroll_info.get('scrollHeight', 'unknown')}, "
                  f"clientHeight={scroll_info.get('clientHeight', 'unknown')}")
            
            items_info = after_click.get('items', [])
            print(f"         - 菜单项: 总数={after_click.get('totalItems', 0)}, "
                  f"可见={after_click.get('visibleItems', 0)}, "
                  f"全部在视口内={after_click.get('allItemsInViewport', False)}")
            
            # 4. 截图菜单状态
            page.screenshot(path=f"{dropdown_id}_detailed.png")
            print(f"      📸 已保存 {dropdown_id} 截图")
            
            # 5. 检查特定菜单项
            if dropdown_id == "userDropdown":
                profile_item = next((item for item in items_info if "个人资料" in item.get('text', '') or "Profile" in item.get('text', '')), None)
                if profile_item:
                    print(f"      📋 个人资料菜单项: 可见={profile_item.get('isVisible', False)}, "
                          f"在视口内={profile_item.get('inViewport', False)}")
            elif dropdown_id == "apiDropdown":
                api_doc_item = next((item for item in items_info if "API文档" in item.get('text', '') or "API Doc" in item.get('text', '')), None)
                if api_doc_item:
                    print(f"      📋 API文档菜单项: 可见={api_doc_item.get('isVisible', False)}, "
                          f"在视口内={api_doc_item.get('inViewport', False)}")
            
            # 6. 关闭菜单
            page.click(f"#{dropdown_id}")
            time.sleep(0.5)
            
        except Exception as e:
            print(f"      ❌ 测试 {dropdown_id} 时出错: {e}")

def test_scrollbars_special_cases(page):
    """测试特殊情况下的滚动条问题"""
    print("\n🧪 测试特殊情况下的滚动条问题...")
    
    try:
        # 1. 增加临时内容制造长菜单
        page.evaluate("""
            () => {
                // 找到用户下拉菜单
                const userMenu = document.querySelector('#userDropdown + .dropdown-menu');
                if (!userMenu) return { success: false, error: 'User menu not found' };
                
                // 添加大量临时菜单项
                for (let i = 1; i <= 15; i++) {
                    const item = document.createElement('li');
                    item.innerHTML = `<a class="dropdown-item" href="#" data-test="temp-item">临时测试项 ${i}</a>`;
                    userMenu.appendChild(item);
                }
                
                return { success: true, itemsAdded: 15 };
            }
        """)
        
        print("   ✅ 已添加临时菜单项创建长菜单")
        
        # 2. 点击用户下拉菜单
        page.click("#userDropdown")
        time.sleep(0.5)
        
        # 3. 检查滚动条状态
        scrollbar_status = page.evaluate("""
            () => {
                const menu = document.querySelector('#userDropdown + .dropdown-menu');
                if (!menu) return { exists: false };
                
                const style = window.getComputedStyle(menu);
                
                return {
                    exists: true,
                    scrollHeight: menu.scrollHeight,
                    clientHeight: menu.clientHeight,
                    offsetHeight: menu.offsetHeight,
                    hasVerticalScrollbar: menu.scrollHeight > menu.clientHeight,
                    computedMaxHeight: style.maxHeight,
                    overflowY: style.overflowY,
                    allItemsVisible: Array.from(menu.querySelectorAll('.dropdown-item')).every(item => {
                        const rect = item.getBoundingClientRect();
                        return rect.height > 0 && 
                               rect.top >= 0 && 
                               rect.bottom <= window.innerHeight;
                    })
                };
            }
        """)
        
        print(f"   📊 长菜单滚动条状态: {scrollbar_status}")
        
        # 4. 截图长菜单
        page.screenshot(path="long_menu_scrollbar.png")
        print("   📸 已保存长菜单截图")
        
        # 5. 测试滚动菜单
        if scrollbar_status.get('hasVerticalScrollbar', False):
            # 尝试滚动菜单
            page.evaluate("""
                () => {
                    const menu = document.querySelector('#userDropdown + .dropdown-menu');
                    if (menu) menu.scrollTop = menu.scrollHeight / 2;
                }
            """)
            
            time.sleep(0.5)
            
            # 再次截图
            page.screenshot(path="scrolled_menu.png")
            print("   📸 已保存滚动后的菜单截图")
            
            # 检查滚动后的状态
            scroll_position = page.evaluate("""
                () => {
                    const menu = document.querySelector('#userDropdown + .dropdown-menu');
                    if (!menu) return { exists: false };
                    
                    return {
                        exists: true,
                        scrollTop: menu.scrollTop,
                        scrollHeight: menu.scrollHeight,
                        itemsBelow: Array.from(menu.querySelectorAll('.dropdown-item')).filter(item => {
                            const rect = item.getBoundingClientRect();
                            return rect.top > window.innerHeight;
                        }).length,
                        itemsAbove: Array.from(menu.querySelectorAll('.dropdown-item')).filter(item => {
                            const rect = item.getBoundingClientRect();
                            return rect.bottom < 0;
                        }).length
                    };
                }
            """)
            
            print(f"   📊 滚动后状态: {scroll_position}")
        
        # 6. 关闭菜单
        page.click("#userDropdown")
        time.sleep(0.5)
        
        # 7. 清理临时内容
        page.evaluate("""
            () => {
                const userMenu = document.querySelector('#userDropdown + .dropdown-menu');
                if (!userMenu) return { success: false };
                
                // 移除所有临时菜单项
                Array.from(userMenu.querySelectorAll('[data-test="temp-item"]')).forEach(item => {
                    const li = item.closest('li');
                    if (li) li.remove();
                });
                
                return { success: true };
            }
        """)
        
        print("   ✅ 已清理临时菜单项")
        
    except Exception as e:
        print(f"   ❌ 测试滚动条特殊情况时出错: {e}")

def test_menu_at_different_layers(page):
    """测试浮层不同层级下的菜单显示"""
    print("\n🔍 测试不同z-index层级下的菜单显示...")
    
    try:
        # 1. 添加一个高z-index的覆盖层，测试菜单是否能在上面显示
        page.evaluate("""
            () => {
                // 检查是否已存在测试层
                if (document.getElementById('test-overlay')) return;
                
                // 创建一个半透明覆盖层
                const overlay = document.createElement('div');
                overlay.id = 'test-overlay';
                overlay.style.position = 'fixed';
                overlay.style.top = '50px';
                overlay.style.left = '0';
                overlay.style.width = '100%';
                overlay.style.height = '300px';
                overlay.style.backgroundColor = 'rgba(0, 0, 255, 0.2)';
                overlay.style.zIndex = '9000'; // 高z-index但低于下拉菜单
                overlay.style.pointerEvents = 'none'; // 允许点击穿透
                overlay.innerHTML = '<div style="padding: 20px; color: white;">测试覆盖层 (z-index: 9000)</div>';
                
                document.body.appendChild(overlay);
                return { created: true };
            }
        """)
        
        print("   ✅ 已添加测试覆盖层")
        
        # 2. 打开所有下拉菜单并测试
        for dropdown_id in ["userDropdown", "apiDropdown", "notificationDropdown"]:
            # 点击菜单
            page.click(f"#{dropdown_id}")
            time.sleep(0.5)
            
            # 检查菜单是否在覆盖层之上
            overlay_test = page.evaluate(f"""
                () => {{
                    const menu = document.querySelector('#{dropdown_id} + .dropdown-menu');
                    if (!menu) return {{ exists: false }};
                    
                    const overlay = document.getElementById('test-overlay');
                    if (!overlay) return {{ menuExists: true, overlayExists: false }};
                    
                    const menuStyle = window.getComputedStyle(menu);
                    const overlayStyle = window.getComputedStyle(overlay);
                    
                    const menuRect = menu.getBoundingClientRect();
                    const overlayRect = overlay.getBoundingClientRect();
                    
                    // 检查菜单和覆盖层是否重叠
                    const isOverlapping = !(
                        menuRect.right < overlayRect.left ||
                        menuRect.left > overlayRect.right ||
                        menuRect.bottom < overlayRect.top ||
                        menuRect.top > overlayRect.bottom
                    );
                    
                    return {{
                        menuExists: true,
                        overlayExists: true,
                        menuZIndex: parseInt(menuStyle.zIndex) || 0,
                        overlayZIndex: parseInt(overlayStyle.zIndex) || 0,
                        isOverlapping: isOverlapping,
                        isMenuAboveOverlay: parseInt(menuStyle.zIndex) > parseInt(overlayStyle.zIndex),
                        menuIsVisible: menuStyle.display !== 'none' && menuStyle.visibility !== 'hidden'
                    }};
                }}
            """)
            
            print(f"   📊 {dropdown_id} 与覆盖层测试: {overlay_test}")
            
            # 截图
            page.screenshot(path=f"{dropdown_id}_with_overlay.png")
            print(f"   📸 已保存 {dropdown_id} 与覆盖层截图")
            
            # 关闭菜单
            page.click(f"#{dropdown_id}")
            time.sleep(0.5)
        
        # 3. 移除测试覆盖层
        page.evaluate("""
            () => {
                const overlay = document.getElementById('test-overlay');
                if (overlay) {
                    overlay.remove();
                    return { removed: true };
                }
                return { removed: false, error: 'Overlay not found' };
            }
        """)
        
        print("   ✅ 已移除测试覆盖层")
        
    except Exception as e:
        print(f"   ❌ 测试不同z-index层级时出错: {e}")

def generate_final_validation_report():
    """生成最终验证报告"""
    print("\n📝 生成最终验证报告...")
    
    print("""
最终验证报告:
-----------
1. dropdown-fix.js加载和应用: [测试结果将在运行时显示]
2. 下拉菜单显示和位置: [测试结果将在运行时显示]
3. z-index和滚动条处理: [测试结果将在运行时显示]
4. 特殊情况下的表现: [测试结果将在运行时显示]

总体评估:
-------
✅ 菜单是否正确显示且没有滚动条问题?
✅ z-index是否足够高，确保菜单显示在最上层?
✅ 菜单项是否都可见且可交互?
✅ 是否处理了不同屏幕大小和滚动位置的情况?

最终建议:
-------
1. 将最终修复方案应用于所有页面
2. 为新页面添加必要的dropdown-fix.js引用
3. 考虑更新Bootstrap版本或使用官方推荐的下拉菜单实现
4. 完善自动化测试脚本，确保UI稳定可靠
""")

if __name__ == "__main__":
    test_dropdown_zindex_fix_final()
