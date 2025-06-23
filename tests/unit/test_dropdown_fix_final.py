"""
验证下拉菜单修复效果的全面测试脚本
特别关注z-index、位置和滚动条问题
"""
import time
from playwright.sync_api import sync_playwright, expect

def test_dropdown_fix_verification():
    with sync_playwright() as p:
        # 测试多种浏览器
        for browser_type in [p.chromium, p.firefox]:
            browser = browser_type.launch(headless=False)
            
            # 测试不同尺寸
            for viewport in [
                {"width": 1920, "height": 1080, "name": "大屏桌面"},
                {"width": 1366, "height": 768, "name": "中屏桌面"},
                {"width": 768, "height": 1024, "name": "平板竖屏"},
                {"width": 414, "height": 896, "name": "手机"}
            ]:
                context = browser.new_context(
                    viewport={"width": viewport["width"], "height": viewport["height"]},
                    record_video_dir="./screenshots/videos/",
                )
                page = context.new_page()
                
                print(f"\n======= 测试 {browser_type.name} - {viewport['name']} ({viewport['width']}x{viewport['height']}) =======")
                
                try:
                    # 访问首页
                    page.goto("http://localhost:8000/")
                    page.wait_for_load_state("networkidle")
                    
                    # 登录
                    if page.url.endswith("/login/"):
                        print("需要登录，正在登录...")
                        page.fill("#id_username", "admin")
                        page.fill("#id_password", "admin")
                        page.click('button[type="submit"]')
                        page.wait_for_load_state("networkidle")
                    
                    # 截图初始状态
                    page.screenshot(path=f"./screenshots/initial_{browser_type.name}_{viewport['name']}.png")
                    
                    # 测试目标下拉菜单
                    dropdowns_to_test = ["userDropdown", "apiDropdown", "notificationDropdown"]
                    
                    # 在移动视图中，可能需要先点击汉堡菜单
                    if viewport["width"] <= 768:
                        print("检测到移动视图，点击汉堡菜单...")
                        page.click("button.navbar-toggler")
                        page.wait_for_timeout(500)
                    
                    # 测试所有下拉菜单
                    for dropdown_id in dropdowns_to_test:
                        # 检查下拉菜单是否存在
                        dropdown_exists = page.evaluate(f"() => !!document.getElementById('{dropdown_id}')")
                        if not dropdown_exists:
                            print(f"❌ {dropdown_id} 不存在，跳过测试")
                            continue
                        
                        print(f"\n测试 {dropdown_id}...")
                        
                        # 获取修复前的Z-Index
                        z_index_before = page.evaluate(f"""() => {{
                            const menu = document.querySelector('#{dropdown_id} + .dropdown-menu');
                            return menu ? getComputedStyle(menu).zIndex : 'not found';
                        }}""")
                        
                        # 点击下拉菜单
                        print(f"点击 {dropdown_id}...")
                        page.click(f"#{dropdown_id}")
                        page.wait_for_timeout(500)
                        
                        # 截图展开状态
                        page.screenshot(path=f"./screenshots/{dropdown_id}_{browser_type.name}_{viewport['name']}.png")
                        
                        # 获取菜单详细信息
                        menu_info = page.evaluate(f"""() => {{
                            const dropdown = document.querySelector('#{dropdown_id} + .dropdown-menu');
                            if (!dropdown) return {{ error: '找不到下拉菜单元素' }};
                            
                            const isShown = dropdown.classList.contains('show');
                            const rect = dropdown.getBoundingClientRect();
                            const style = getComputedStyle(dropdown);
                            
                            // 检查菜单项
                            const items = Array.from(dropdown.querySelectorAll('.dropdown-item, .dropdown-header, .dropdown-divider'));
                            const itemsInfo = items.map(item => {{
                                const itemRect = item.getBoundingClientRect();
                                return {{
                                    text: item.textContent.trim(),
                                    visible: getComputedStyle(item).display !== 'none' && getComputedStyle(item).visibility !== 'hidden',
                                    display: getComputedStyle(item).display,
                                    inViewport: (
                                        itemRect.top >= 0 &&
                                        itemRect.left >= 0 &&
                                        itemRect.bottom <= window.innerHeight &&
                                        itemRect.right <= window.innerWidth
                                    )
                                }};
                            }});
                            
                            return {{
                                shown: isShown,
                                display: style.display,
                                visibility: style.visibility,
                                position: style.position,
                                zIndex: style.zIndex,
                                transform: style.transform,
                                overflow: style.overflow,
                                maxHeight: style.maxHeight,
                                dimensions: {{
                                    top: rect.top,
                                    left: rect.left,
                                    width: rect.width,
                                    height: rect.height,
                                    right: rect.right,
                                    bottom: rect.bottom
                                }},
                                itemsCount: items.length,
                                visibleItemsCount: itemsInfo.filter(i => i.visible).length,
                                allItemsVisible: itemsInfo.every(i => i.visible),
                                hasScrollbar: dropdown.scrollHeight > dropdown.clientHeight,
                                allItemsInViewport: itemsInfo.every(i => i.inViewport)
                            }};
                        }}""")
                        
                        # 输出详细信息
                        print(f"{dropdown_id} 详情:")
                        print(f"显示状态: {menu_info.get('shown', False)}")
                        print(f"显示属性: {menu_info.get('display', 'unknown')}")
                        print(f"可见性: {menu_info.get('visibility', 'unknown')}")
                        print(f"定位方式: {menu_info.get('position', 'unknown')}")
                        print(f"Z-Index: {menu_info.get('zIndex', 'unknown')} (之前: {z_index_before})")
                        print(f"溢出处理: {menu_info.get('overflow', 'unknown')}")
                        print(f"最大高度: {menu_info.get('maxHeight', 'unknown')}")
                        
                        # 检查位置
                        dimensions = menu_info.get('dimensions', {})
                        if dimensions:
                            print(f"位置: 顶部={dimensions.get('top')}, 左侧={dimensions.get('left')}, 宽度={dimensions.get('width')}, 高度={dimensions.get('height')}")
                            
                            # 验证是否在视口内
                            in_viewport = (
                                dimensions.get('top', 0) >= 0 and
                                dimensions.get('left', 0) >= 0 and
                                dimensions.get('bottom', 0) <= viewport['height'] and
                                dimensions.get('right', 0) <= viewport['width']
                            )
                            print(f"菜单在视口内: {in_viewport}")
                        
                        # 检查菜单项
                        print(f"菜单项总数: {menu_info.get('itemsCount', 0)}")
                        print(f"可见菜单项数: {menu_info.get('visibleItemsCount', 0)}")
                        print(f"所有菜单项可见: {menu_info.get('allItemsVisible', False)}")
                        print(f"所有菜单项在视口内: {menu_info.get('allItemsInViewport', False)}")
                        print(f"有滚动条: {menu_info.get('hasScrollbar', False)}")
                        
                        # 测试点击菜单项
                        print("\n测试点击菜单项...")
                        # 找到第一个可点击的菜单项
                        first_item = page.evaluate(f"""() => {{
                            const items = document.querySelectorAll('#{dropdown_id} + .dropdown-menu .dropdown-item');
                            for (const item of items) {{
                                if (getComputedStyle(item).display !== 'none' && 
                                    getComputedStyle(item).visibility !== 'hidden') {{
                                    return {{
                                        text: item.textContent.trim(),
                                        href: item.getAttribute('href')
                                    }};
                                }}
                            }}
                            return null;
                        }}""")
                        
                        if first_item:
                            print(f"尝试点击菜单项: {first_item.get('text', 'unknown')}")
                            
                            try:
                                # 获取当前URL以便对比
                                current_url = page.url
                                
                                # 尝试点击第一个菜单项
                                page.click(f"#{dropdown_id} + .dropdown-menu .dropdown-item:first-child", timeout=2000)
                                page.wait_for_timeout(1000)
                                
                                # 检查URL是否改变
                                new_url = page.url
                                if new_url != current_url:
                                    print(f"✅ 成功导航到新页面: {new_url}")
                                else:
                                    print(f"❌ 点击后URL未改变: {new_url}")
                                
                                # 返回首页
                                page.goto("http://localhost:8000/")
                                page.wait_for_load_state("networkidle")
                                
                                # 在移动视图中，可能需要再次点击汉堡菜单
                                if viewport["width"] <= 768:
                                    page.click("button.navbar-toggler")
                                    page.wait_for_timeout(500)
                            
                            except Exception as e:
                                print(f"❌ 点击菜单项失败: {e}")
                        else:
                            print("❌ 未找到可点击的菜单项")
                        
                        # 如果仍在展开状态，关闭下拉菜单
                        is_expanded = page.evaluate(f"""() => {{
                            const dropdown = document.getElementById('{dropdown_id}');
                            return dropdown && dropdown.getAttribute('aria-expanded') === 'true';
                        }}""")
                        
                        if is_expanded:
                            print(f"关闭 {dropdown_id}...")
                            page.click(f"#{dropdown_id}")
                            page.wait_for_timeout(500)
                    
                    # 测试下拉菜单交互（打开多个）
                    if len(dropdowns_to_test) >= 2:
                        print("\n测试下拉菜单交互...")
                        
                        # 打开第一个下拉菜单
                        first_dropdown = dropdowns_to_test[0]
                        first_exists = page.evaluate(f"() => !!document.getElementById('{first_dropdown}')")
                        
                        if first_exists:
                            print(f"打开 {first_dropdown}...")
                            page.click(f"#{first_dropdown}")
                            page.wait_for_timeout(500)
                            
                            # 验证第一个下拉菜单已打开
                            first_shown = page.evaluate(f"""() => {{
                                const menu = document.querySelector('#{first_dropdown} + .dropdown-menu');
                                return menu && menu.classList.contains('show');
                            }}""")
                            
                            print(f"{first_dropdown} 已打开: {first_shown}")
                            
                            # 打开第二个下拉菜单
                            second_dropdown = dropdowns_to_test[1]
                            second_exists = page.evaluate(f"() => !!document.getElementById('{second_dropdown}')")
                            
                            if second_exists:
                                print(f"打开 {second_dropdown}...")
                                page.click(f"#{second_dropdown}")
                                page.wait_for_timeout(500)
                                
                                # 验证第一个下拉菜单已关闭，第二个已打开
                                results = page.evaluate(f"""() => {{
                                    const firstMenu = document.querySelector('#{first_dropdown} + .dropdown-menu');
                                    const secondMenu = document.querySelector('#{second_dropdown} + .dropdown-menu');
                                    
                                    return {{
                                        firstShown: firstMenu && firstMenu.classList.contains('show'),
                                        secondShown: secondMenu && secondMenu.classList.contains('show')
                                    }};
                                }}""")
                                
                                print(f"{first_dropdown} 仍然打开: {results.get('firstShown', False)}")
                                print(f"{second_dropdown} 已打开: {results.get('secondShown', False)}")
                                
                                # 验证正确性
                                if not results.get('firstShown', True) and results.get('secondShown', False):
                                    print("✅ 下拉菜单交互正确：点击第二个菜单时，第一个菜单自动关闭")
                                else:
                                    print("❌ 下拉菜单交互问题：第一个菜单未正确关闭或第二个菜单未正确打开")
                                
                                # 截图当前状态
                                page.screenshot(path=f"./screenshots/dropdown_interaction_{browser_type.name}_{viewport['name']}.png")
                                
                                # 关闭第二个下拉菜单
                                page.click(f"#{second_dropdown}")
                                page.wait_for_timeout(500)
                    
                    # 最终验证 - 点击页面其他区域是否关闭下拉菜单
                    print("\n测试点击页面其他区域关闭下拉菜单...")
                    
                    # 选择第一个可用的下拉菜单
                    for dropdown_id in dropdowns_to_test:
                        dropdown_exists = page.evaluate(f"() => !!document.getElementById('{dropdown_id}')")
                        if dropdown_exists:
                            # 打开下拉菜单
                            print(f"打开 {dropdown_id}...")
                            page.click(f"#{dropdown_id}")
                            page.wait_for_timeout(500)
                            
                            # 验证下拉菜单已打开
                            is_shown = page.evaluate(f"""() => {{
                                const menu = document.querySelector('#{dropdown_id} + .dropdown-menu');
                                return menu && menu.classList.contains('show');
                            }}""")
                            
                            if is_shown:
                                # 点击页面空白区域
                                print("点击页面空白区域...")
                                page.click("body", position={"x": 10, "y": 10})
                                page.wait_for_timeout(500)
                                
                                # 检查下拉菜单是否已关闭
                                is_closed = page.evaluate(f"""() => {{
                                    const menu = document.querySelector('#{dropdown_id} + .dropdown-menu');
                                    return !(menu && menu.classList.contains('show'));
                                }}""")
                                
                                if is_closed:
                                    print("✅ 点击页面其他区域成功关闭下拉菜单")
                                else:
                                    print("❌ 点击页面其他区域未能关闭下拉菜单")
                            
                            # 只测试第一个可用的下拉菜单
                            break
                    
                    print("\n测试完成")
                
                except Exception as e:
                    print(f"测试过程中出错: {e}")
                    page.screenshot(path=f"./screenshots/error_{browser_type.name}_{viewport['name']}.png")
                
                finally:
                    # 关闭上下文
                    context.close()
            
            # 关闭浏览器
            browser.close()

if __name__ == "__main__":
    test_dropdown_fix_verification()
