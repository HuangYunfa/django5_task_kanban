#!/usr/bin/env python3
"""
下拉菜单z-index和滚动条问题诊断脚本
专门检测并解决下拉菜单的层叠顺序和滚动条问题
"""

import time
import sys
from playwright.sync_api import sync_playwright, expect

def test_dropdown_zindex_and_scroll():
    """测试下拉菜单z-index和滚动条问题"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=300)
        context = browser.new_context()
        page = context.new_page()
        
        print("=" * 70)
        print("下拉菜单z-index和滚动条问题诊断")
        print("=" * 70)
        
        try:
            # 1. 登录
            login(page)
            
            # 2. 检查各下拉菜单的z-index和滚动条
            check_dropdown_zindex(page, "user")
            check_dropdown_zindex(page, "api")
            check_dropdown_zindex(page, "notification")
            
            # 3. 检查下拉菜单是否被其他元素遮挡
            check_dropdown_overlay(page)
            
            # 4. 模拟不同窗口大小下的表现
            test_responsive_behavior(page)
            
            # 5. 尝试强制修复并验证
            force_fix_and_verify(page)
            
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

def check_dropdown_zindex(page, dropdown_type):
    """检查特定下拉菜单的z-index和滚动条"""
    dropdown_id = f"{dropdown_type}Dropdown"
    print(f"\n🔍 检查{dropdown_type}下拉菜单的z-index和滚动条...")
    
    # 点击下拉菜单
    try:
        page.click(f"#{dropdown_id}")
        time.sleep(0.5)
        
        # 获取下拉菜单的计算样式
        dropdown_styles = page.evaluate(f"""
            () => {{
                const menu = document.querySelector('#{dropdown_id} + .dropdown-menu');
                if (!menu) return {{ exists: false }};
                
                const style = window.getComputedStyle(menu);
                const rect = menu.getBoundingClientRect();
                
                // 检查是否有滚动条
                const hasVerticalScrollbar = menu.scrollHeight > menu.clientHeight;
                const hasHorizontalScrollbar = menu.scrollWidth > menu.clientWidth;
                
                return {{
                    exists: true,
                    zIndex: style.zIndex,
                    position: style.position,
                    display: style.display,
                    visibility: style.visibility,
                    overflow: style.overflow,
                    overflowY: style.overflowY,
                    overflowX: style.overflowX,
                    maxHeight: style.maxHeight,
                    height: style.height,
                    top: style.top,
                    right: style.right,
                    left: style.left,
                    
                    // 位置和尺寸
                    rect: {{
                        top: rect.top,
                        left: rect.left,
                        bottom: rect.bottom,
                        right: rect.right,
                        width: rect.width,
                        height: rect.height
                    }},
                    
                    // 滚动信息
                    hasVerticalScrollbar,
                    hasHorizontalScrollbar,
                    scrollHeight: menu.scrollHeight,
                    clientHeight: menu.clientHeight,
                    scrollWidth: menu.scrollWidth,
                    clientWidth: menu.clientWidth
                }};
            }}
        """)
        
        print(f"   📊 {dropdown_type}下拉菜单样式: {dropdown_styles}")
        
        # 如果存在滚动条，检查是否是必要的
        if dropdown_styles.get('exists', False):
            if dropdown_styles.get('hasVerticalScrollbar', False):
                print(f"   ⚠️ 警告: {dropdown_type}下拉菜单存在垂直滚动条")
                print(f"   📏 菜单高度: {dropdown_styles.get('clientHeight')}px, 内容高度: {dropdown_styles.get('scrollHeight')}px")
            
            if dropdown_styles.get('hasHorizontalScrollbar', False):
                print(f"   ⚠️ 警告: {dropdown_type}下拉菜单存在水平滚动条")
                print(f"   📏 菜单宽度: {dropdown_styles.get('clientWidth')}px, 内容宽度: {dropdown_styles.get('scrollWidth')}px")
        
        # 获取菜单项信息
        menu_items = page.evaluate(f"""
            () => {{
                const menu = document.querySelector('#{dropdown_id} + .dropdown-menu');
                if (!menu) return {{ exists: false }};
                
                const items = Array.from(menu.querySelectorAll('.dropdown-item, .dropdown-header, .dropdown-divider, .dropdown-item-text'));
                return {{
                    exists: true,
                    itemCount: items.length,
                    items: items.map(item => {{
                        const style = window.getComputedStyle(item);
                        return {{
                            text: item.innerText.trim(),
                            type: item.tagName.toLowerCase(),
                            classes: item.className,
                            display: style.display,
                            visibility: style.visibility,
                            height: style.height,
                            overflow: style.overflow
                        }};
                    }})
                }};
            }}
        """)
        
        print(f"   📋 {dropdown_type}下拉菜单项: {menu_items}")
        
        # 尝试截图
        page.screenshot(path=f"{dropdown_type}_dropdown_zindex.png")
        print(f"   📸 已保存{dropdown_type}下拉菜单截图")
        
        # 关闭下拉菜单
        page.click(f"#{dropdown_id}")
        time.sleep(0.5)
        
    except Exception as e:
        print(f"   ❌ 检查{dropdown_type}下拉菜单时出错: {e}")

def check_dropdown_overlay(page):
    """检查下拉菜单是否被其他元素遮挡"""
    print("\n🔍 检查下拉菜单是否被其他元素遮挡...")
    
    try:
        # 检查页面上所有可能与下拉菜单重叠的元素
        overlapping_elements = page.evaluate("""
            () => {
                // 获取所有下拉菜单的位置
                const dropdowns = ['userDropdown', 'apiDropdown', 'notificationDropdown'];
                const dropdownElements = {};
                
                dropdowns.forEach(id => {
                    const trigger = document.getElementById(id);
                    if (trigger) {
                        const menu = trigger.nextElementSibling;
                        if (menu && menu.classList.contains('dropdown-menu')) {
                            // 获取触发器位置
                            dropdownElements[id] = {
                                trigger: trigger.getBoundingClientRect(),
                                menu: null
                            };
                        }
                    }
                });
                
                // 获取页面上所有元素，检查z-index高于下拉菜单的元素
                const allElements = Array.from(document.querySelectorAll('*'));
                const potentialOverlaps = allElements.filter(el => {
                    const style = window.getComputedStyle(el);
                    const zIndex = parseInt(style.zIndex, 10);
                    return !isNaN(zIndex) && zIndex > 1000 && style.position !== 'static';
                }).map(el => ({
                    tagName: el.tagName,
                    id: el.id,
                    className: el.className,
                    zIndex: window.getComputedStyle(el).zIndex,
                    position: window.getComputedStyle(el).position
                }));
                
                return {
                    dropdownElements,
                    potentialOverlaps
                };
            }
        """)
        
        print(f"   📊 下拉菜单位置: {overlapping_elements.get('dropdownElements', {})}")
        print(f"   📊 可能重叠的元素: {overlapping_elements.get('potentialOverlaps', [])}")
        
        # 依次点击每个下拉菜单，并检查是否被其他元素遮挡
        for dropdown_id in ['userDropdown', 'apiDropdown', 'notificationDropdown']:
            page.click(f"#{dropdown_id}")
            time.sleep(0.5)
            
            # 尝试检查菜单项是否可点击
            clickable = page.evaluate(f"""
                () => {{
                    const menu = document.querySelector('#{dropdown_id} + .dropdown-menu');
                    if (!menu) return {{ exists: false }};
                    
                    const items = Array.from(menu.querySelectorAll('.dropdown-item'));
                    if (items.length === 0) return {{ exists: true, hasItems: false }};
                    
                    // 获取第一个菜单项
                    const firstItem = items[0];
                    const rect = firstItem.getBoundingClientRect();
                    
                    // 检查此位置是否有其他元素
                    const centerX = rect.left + rect.width / 2;
                    const centerY = rect.top + rect.height / 2;
                    const elementAtPoint = document.elementFromPoint(centerX, centerY);
                    
                    return {{
                        exists: true,
                        hasItems: true,
                        firstItemText: firstItem.innerText,
                        isClickable: elementAtPoint === firstItem || firstItem.contains(elementAtPoint),
                        elementAtPoint: elementAtPoint ? {{
                            tagName: elementAtPoint.tagName,
                            id: elementAtPoint.id,
                            className: elementAtPoint.className
                        }} : null
                    }};
                }}
            """)
            
            print(f"   🖱️ {dropdown_id}菜单项可点击性: {clickable}")
            
            # 关闭下拉菜单
            page.click(f"#{dropdown_id}")
            time.sleep(0.5)
        
    except Exception as e:
        print(f"   ❌ 检查下拉菜单重叠时出错: {e}")

def test_responsive_behavior(page):
    """测试不同窗口大小下的下拉菜单表现"""
    print("\n📱 测试响应式表现...")
    
    # 测试不同屏幕尺寸
    screen_sizes = [
        {"width": 375, "height": 667, "name": "手机"},
        {"width": 768, "height": 1024, "name": "平板"},
        {"width": 1280, "height": 800, "name": "桌面"}
    ]
    
    for size in screen_sizes:
        try:
            print(f"\n   🖥️ 测试{size['name']}尺寸 ({size['width']}x{size['height']})...")
            page.set_viewport_size({"width": size['width'], "height": size['height']})
            time.sleep(1)
            
            # 如果是小屏幕，可能需要点击汉堡菜单
            if size['width'] < 992:
                if page.locator(".navbar-toggler").is_visible():
                    page.click(".navbar-toggler")
                    time.sleep(0.5)
            
            # 测试每个下拉菜单
            for dropdown_id in ['userDropdown', 'apiDropdown', 'notificationDropdown']:
                if page.locator(f"#{dropdown_id}").is_visible():
                    page.click(f"#{dropdown_id}")
                    time.sleep(0.5)
                    
                    # 检查下拉菜单在当前尺寸下的表现
                    menu_behavior = page.evaluate(f"""
                        () => {{
                            const menu = document.querySelector('#{dropdown_id} + .dropdown-menu');
                            if (!menu) return {{ exists: false }};
                            
                            const style = window.getComputedStyle(menu);
                            const rect = menu.getBoundingClientRect();
                            
                            // 检查菜单是否超出屏幕
                            const viewportWidth = window.innerWidth;
                            const viewportHeight = window.innerHeight;
                            const isOffscreenRight = rect.right > viewportWidth;
                            const isOffscreenBottom = rect.bottom > viewportHeight;
                            
                            return {{
                                exists: true,
                                position: style.position,
                                display: style.display,
                                rect: {{
                                    top: rect.top,
                                    left: rect.left,
                                    bottom: rect.bottom,
                                    right: rect.right,
                                    width: rect.width,
                                    height: rect.height
                                }},
                                viewport: {{ width: viewportWidth, height: viewportHeight }},
                                isOffscreenRight,
                                isOffscreenBottom
                            }};
                        }}
                    """)
                    
                    print(f"   📊 {size['name']}尺寸下{dropdown_id}菜单表现: {menu_behavior}")
                    
                    # 截图
                    page.screenshot(path=f"{dropdown_id}_{size['name']}.png")
                    
                    # 关闭下拉菜单
                    page.click(f"#{dropdown_id}")
                    time.sleep(0.5)
                else:
                    print(f"   ⚠️ {dropdown_id}在{size['name']}尺寸下不可见")
            
            # 如果是小屏幕，关闭汉堡菜单
            if size['width'] < 992:
                if page.locator(".navbar-toggler").is_visible():
                    page.click(".navbar-toggler")
                    time.sleep(0.5)
            
        except Exception as e:
            print(f"   ❌ 测试{size['name']}尺寸时出错: {e}")
    
    # 恢复桌面视图
    page.set_viewport_size({"width": 1280, "height": 800})

def force_fix_and_verify(page):
    """强制修复z-index和滚动条问题并验证"""
    print("\n🛠️ 强制修复z-index和滚动条问题...")
    
    try:
        # 注入更强力的修复脚本
        fix_result = page.evaluate("""
            () => {
                // 应用更强力的样式修复
                const style = document.createElement('style');
                style.textContent = `
                    /* 强制修复z-index和滚动条问题 */
                    .dropdown-menu.show {
                        display: block !important;
                        visibility: visible !important;
                        opacity: 1 !important;
                        z-index: 99999 !important;
                        position: absolute !important;
                        overflow: visible !important;
                        transform: none !important;
                        max-height: none !important;
                        min-height: auto !important;
                    }
                    
                    /* 确保下拉菜单不被任何元素裁剪 */
                    body, .navbar, .navbar-collapse, .navbar-nav, .nav-item, .dropdown {
                        overflow: visible !important;
                    }
                    
                    /* 用户和通知下拉菜单右对齐 */
                    #userDropdown + .dropdown-menu.show,
                    #notificationDropdown + .dropdown-menu.show {
                        right: 0 !important;
                        left: auto !important;
                    }
                    
                    /* API下拉菜单左对齐 */
                    #apiDropdown + .dropdown-menu.show {
                        left: 0 !important;
                        right: auto !important;
                    }
                `;
                document.head.appendChild(style);
                
                // 强制所有下拉菜单在点击时正确显示
                const fixDropdowns = (dropdownId) => {
                    const trigger = document.getElementById(dropdownId);
                    if (!trigger) return false;
                    
                    const menu = trigger.nextElementSibling;
                    if (!menu || !menu.classList.contains('dropdown-menu')) return false;
                    
                    // 强制移除所有影响显示的样式
                    const forceShowMenu = () => {
                        menu.classList.add('show');
                        menu.style.display = 'block';
                        menu.style.visibility = 'visible';
                        menu.style.opacity = '1';
                        menu.style.zIndex = '99999';
                        menu.style.maxHeight = 'none';
                        menu.style.overflow = 'visible';
                        menu.style.position = 'absolute';
                        
                        // 确保所有菜单项可见
                        menu.querySelectorAll('.dropdown-item, .dropdown-header, .dropdown-divider, .dropdown-item-text').forEach(item => {
                            item.style.display = 'block';
                            item.style.visibility = 'visible';
                            item.style.opacity = '1';
                        });
                    };
                    
                    // 拦截事件，确保菜单显示
                    const originalToggle = trigger.onclick;
                    trigger.onclick = (e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        
                        if (menu.classList.contains('show')) {
                            menu.classList.remove('show');
                            menu.style.display = 'none';
                        } else {
                            // 关闭其他菜单
                            document.querySelectorAll('.dropdown-menu.show').forEach(openMenu => {
                                if (openMenu !== menu) {
                                    openMenu.classList.remove('show');
                                    openMenu.style.display = 'none';
                                }
                            });
                            
                            forceShowMenu();
                        }
                    };
                    
                    return true;
                };
                
                // 应用到所有下拉菜单
                const results = {
                    userDropdown: fixDropdowns('userDropdown'),
                    apiDropdown: fixDropdowns('apiDropdown'),
                    notificationDropdown: fixDropdowns('notificationDropdown')
                };
                
                return {
                    styleAdded: true,
                    fixResults: results
                };
            }
        """)
        
        print(f"   📊 强制修复结果: {fix_result}")
        
        # 测试修复后的下拉菜单
        print("\n   🧪 测试修复后的下拉菜单...")
        
        for dropdown_id in ['userDropdown', 'apiDropdown', 'notificationDropdown']:
            # 点击下拉菜单
            page.click(f"#{dropdown_id}")
            time.sleep(0.5)
            
            # 截图记录修复后的状态
            page.screenshot(path=f"{dropdown_id}_fixed.png")
            print(f"   📸 已保存修复后的{dropdown_id}菜单截图")
            
            # 检查修复效果
            fixed_status = page.evaluate(f"""
                () => {{
                    const menu = document.querySelector('#{dropdown_id} + .dropdown-menu');
                    if (!menu) return {{ exists: false }};
                    
                    const style = window.getComputedStyle(menu);
                    const rect = menu.getBoundingClientRect();
                    
                    // 检查菜单项可点击性
                    const items = Array.from(menu.querySelectorAll('.dropdown-item'));
                    const itemsStatus = items.map(item => {{
                        const itemRect = item.getBoundingClientRect();
                        const centerX = itemRect.left + itemRect.width / 2;
                        const centerY = itemRect.top + itemRect.height / 2;
                        const elementAtPoint = document.elementFromPoint(centerX, centerY);
                        
                        return {{
                            text: item.innerText.trim(),
                            isPointingToItem: elementAtPoint === item || item.contains(elementAtPoint)
                        }};
                    }});
                    
                    return {{
                        exists: true,
                        isVisible: style.display !== 'none' && style.visibility !== 'hidden',
                        zIndex: style.zIndex,
                        position: style.position,
                        hasVerticalScrollbar: menu.scrollHeight > menu.clientHeight,
                        itemsStatus
                    }};
                }}
            """)
            
            print(f"   📊 修复后{dropdown_id}菜单状态: {fixed_status}")
            
            # 关闭下拉菜单
            page.click(f"#{dropdown_id}")
            time.sleep(0.5)
        
    except Exception as e:
        print(f"   ❌ 强制修复时出错: {e}")

if __name__ == "__main__":
    test_dropdown_zindex_and_scroll()
