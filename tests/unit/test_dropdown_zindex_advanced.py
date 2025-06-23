"""
详细测试下拉菜单z-index和位置问题
特别关注滚动条出现和菜单项可见性问题
"""
import time
from playwright.sync_api import sync_playwright, expect

def test_dropdown_zindex_and_position():
    with sync_playwright() as p:
        # 测试桌面和移动设备
        for browser_type in [p.chromium, p.firefox]:
            # 针对每种浏览器类型运行测试
            browser = browser_type.launch(headless=False)
            
            # 测试不同视窗大小
            for viewport in [
                {"width": 1920, "height": 1080, "name": "桌面大屏"},
                {"width": 1366, "height": 768, "name": "桌面中屏"},
                {"width": 768, "height": 1024, "name": "平板"},
                {"width": 414, "height": 896, "name": "手机"}
            ]:
                context = browser.new_context(
                    viewport={"width": viewport["width"], "height": viewport["height"]},
                    record_video_dir="./screenshots/videos/",
                )
                page = context.new_page()
                
                print(f"\n======= 测试 {browser_type.name} - {viewport['name']} =======")
                
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
                    
                    # 截图整个页面，作为参考
                    page.screenshot(path=f"./screenshots/before_dropdown_{browser_type.name}_{viewport['name']}.png")
                    
                    # 测试用户下拉菜单
                    print("测试用户下拉菜单...")
                    
                    # 捕获点击前的z-index和位置信息
                    z_index_before = page.evaluate("""() => {
                        const dropdown = document.querySelector('#userDropdown + .dropdown-menu');
                        return dropdown ? getComputedStyle(dropdown).zIndex : 'not found';
                    }""")
                    
                    # 点击用户下拉菜单
                    page.click("#userDropdown")
                    page.wait_for_timeout(500)  # 等待动画完成
                    
                    # 截图菜单展开状态
                    page.screenshot(path=f"./screenshots/user_dropdown_{browser_type.name}_{viewport['name']}.png")
                    
                    # 获取下拉菜单详细信息
                    dropdown_info = page.evaluate("""() => {
                        const dropdown = document.querySelector('#userDropdown + .dropdown-menu.show');
                        if (!dropdown) return { error: 'Dropdown menu not found or not showing' };
                        
                        const rect = dropdown.getBoundingClientRect();
                        const style = getComputedStyle(dropdown);
                        
                        // 检查所有菜单项
                        const items = Array.from(dropdown.querySelectorAll('.dropdown-item, .dropdown-divider'));
                        const itemsInfo = items.map(item => {
                            const itemRect = item.getBoundingClientRect();
                            const itemStyle = getComputedStyle(item);
                            
                            return {
                                text: item.textContent.trim(),
                                visible: itemStyle.display !== 'none' && itemStyle.visibility !== 'hidden',
                                display: itemStyle.display,
                                visibility: itemStyle.visibility,
                                position: {
                                    top: itemRect.top,
                                    left: itemRect.left,
                                    width: itemRect.width,
                                    height: itemRect.height,
                                    inViewport: (
                                        itemRect.top >= 0 &&
                                        itemRect.left >= 0 &&
                                        itemRect.bottom <= window.innerHeight &&
                                        itemRect.right <= window.innerWidth
                                    )
                                }
                            };
                        });
                        
                        return {
                            exists: true,
                            shown: dropdown.classList.contains('show'),
                            display: style.display,
                            visibility: style.visibility,
                            position: style.position,
                            zIndex: style.zIndex,
                            overflow: style.overflow,
                            dimensions: {
                                top: rect.top,
                                left: rect.left,
                                right: rect.right,
                                bottom: rect.bottom,
                                width: rect.width,
                                height: rect.height
                            },
                            maxHeight: style.maxHeight,
                            overflowY: style.overflowY,
                            scrollHeight: dropdown.scrollHeight,
                            clientHeight: dropdown.clientHeight,
                            hasScrollbar: dropdown.scrollHeight > dropdown.clientHeight,
                            items: itemsInfo,
                            itemsCount: items.length,
                            visibleItemsCount: itemsInfo.filter(i => i.visible).length
                        };
                    }""")
                    
                    print(f"\n用户下拉菜单详情:")
                    print(f"存在: {dropdown_info.get('exists', False)}")
                    print(f"显示状态: {dropdown_info.get('shown', False)}")
                    print(f"显示属性: {dropdown_info.get('display', 'unknown')}")
                    print(f"可见性: {dropdown_info.get('visibility', 'unknown')}")
                    print(f"定位方式: {dropdown_info.get('position', 'unknown')}")
                    print(f"Z-Index: {dropdown_info.get('zIndex', 'unknown')} (点击前: {z_index_before})")
                    print(f"溢出控制: {dropdown_info.get('overflow', 'unknown')}")
                    
                    dimensions = dropdown_info.get('dimensions', {})
                    if dimensions:
                        print(f"位置和尺寸: 顶部={dimensions.get('top')}, 左侧={dimensions.get('left')}, 宽度={dimensions.get('width')}, 高度={dimensions.get('height')}")
                    
                    print(f"最大高度: {dropdown_info.get('maxHeight', 'unknown')}")
                    print(f"垂直溢出: {dropdown_info.get('overflowY', 'unknown')}")
                    print(f"内容高度: {dropdown_info.get('scrollHeight', 'unknown')}")
                    print(f"视口高度: {dropdown_info.get('clientHeight', 'unknown')}")
                    print(f"是否有滚动条: {dropdown_info.get('hasScrollbar', 'unknown')}")
                    print(f"菜单项总数: {dropdown_info.get('itemsCount', 0)}")
                    print(f"可见菜单项数: {dropdown_info.get('visibleItemsCount', 0)}")
                    
                    # 检查菜单项详情
                    items = dropdown_info.get('items', [])
                    if items:
                        print("\n菜单项详情:")
                        for i, item in enumerate(items):
                            print(f"  {i+1}. {item.get('text', 'No text')} - 可见: {item.get('visible', False)}, 显示方式: {item.get('display', 'unknown')}")
                            pos = item.get('position', {})
                            if pos:
                                print(f"     位于视口内: {pos.get('inViewport', False)}, 位置: 顶部={pos.get('top')}, 左侧={pos.get('left')}")
                    
                    # 检查点击菜单项是否工作
                    # 首先检查"个人资料"是否存在且可见
                    profile_link_visible = page.evaluate("""() => {
                        const link = Array.from(document.querySelectorAll('#userDropdown + .dropdown-menu .dropdown-item'))
                            .find(el => el.textContent.trim().includes('个人资料') || el.textContent.trim().includes('Profile'));
                        return link && 
                               getComputedStyle(link).display !== 'none' && 
                               getComputedStyle(link).visibility !== 'hidden';
                    }""")
                    
                    if profile_link_visible:
                        print("\n尝试点击'个人资料'菜单项...")
                        try:
                            # 使用文本内容找到并点击菜单项
                            page.click("text=个人资料", timeout=2000)
                            page.wait_for_timeout(1000)
                            
                            # 验证是否成功导航到个人资料页面
                            current_url = page.url
                            if "/profile/" in current_url:
                                print("✅ 成功导航到个人资料页面!")
                            else:
                                print(f"❌ 未导航到个人资料页面。当前URL: {current_url}")
                        except Exception as e:
                            print(f"❌ 点击'个人资料'失败: {e}")
                    else:
                        print("❌ '个人资料'菜单项不可见或不存在")
                        
                    # 返回主页
                    page.goto("http://localhost:8000/")
                    page.wait_for_load_state("networkidle")
                    
                    # 测试其他下拉菜单
                    for dropdown_id in ["apiDropdown", "notificationDropdown"]:
                        try:
                            # 检查下拉菜单是否存在
                            dropdown_exists = page.evaluate(f"() => !!document.getElementById('{dropdown_id}')")
                            if not dropdown_exists:
                                print(f"\n❌ {dropdown_id} 不存在")
                                continue
                                
                            print(f"\n测试 {dropdown_id}...")
                            page.click(f"#{dropdown_id}")
                            page.wait_for_timeout(500)
                            
                            # 截图菜单展开状态
                            page.screenshot(path=f"./screenshots/{dropdown_id}_{browser_type.name}_{viewport['name']}.png")
                            
                            # 获取下拉菜单信息
                            menu_info = page.evaluate(f"""() => {{
                                const dropdown = document.querySelector('#{dropdown_id} + .dropdown-menu.show');
                                if (!dropdown) return {{ error: 'Dropdown menu not found or not showing' }};
                                
                                const rect = dropdown.getBoundingClientRect();
                                const style = getComputedStyle(dropdown);
                                
                                return {{
                                    exists: true,
                                    shown: dropdown.classList.contains('show'),
                                    display: style.display,
                                    visibility: style.visibility,
                                    position: style.position,
                                    zIndex: style.zIndex,
                                    dimensions: {{
                                        top: rect.top,
                                        left: rect.left,
                                        width: rect.width,
                                        height: rect.height
                                    }},
                                    hasScrollbar: dropdown.scrollHeight > dropdown.clientHeight,
                                    itemsCount: dropdown.querySelectorAll('.dropdown-item').length,
                                    visibleItemsCount: Array.from(dropdown.querySelectorAll('.dropdown-item')).filter(
                                        item => getComputedStyle(item).display !== 'none' && getComputedStyle(item).visibility !== 'hidden'
                                    ).length
                                }};
                            }})""")
                            
                            print(f"{dropdown_id} 详情:")
                            print(f"显示状态: {menu_info.get('shown', False)}")
                            print(f"Z-Index: {menu_info.get('zIndex', 'unknown')}")
                            print(f"是否有滚动条: {menu_info.get('hasScrollbar', 'unknown')}")
                            print(f"菜单项总数: {menu_info.get('itemsCount', 0)}")
                            print(f"可见菜单项数: {menu_info.get('visibleItemsCount', 0)}")
                            
                        except Exception as e:
                            print(f"❌ 测试 {dropdown_id} 失败: {e}")
                    
                except Exception as e:
                    print(f"测试过程中出错: {e}")
                    page.screenshot(path=f"./screenshots/error_{browser_type.name}_{viewport['name']}.png")
                
                finally:
                    context.close()
            
            browser.close()

if __name__ == "__main__":
    test_dropdown_zindex_and_position()
