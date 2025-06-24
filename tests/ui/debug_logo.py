#!/usr/bin/env python3
"""
详细的logo调试测试
"""

import time
import sys
import os
from playwright.sync_api import sync_playwright

def debug_logo_issue():
    """详细调试logo显示问题"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=1000)
        context = browser.new_context(viewport={'width': 1280, 'height': 720})
        page = context.new_page()
        
        try:
            print("🔍 详细调试logo显示问题...")
            
            # 访问首页
            page.goto('http://127.0.0.1:8000/')
            page.wait_for_load_state('networkidle', timeout=10000)
            time.sleep(2)
            
            # 检查完整的navbar-brand HTML
            print("\n📋 完整的navbar-brand HTML:")
            navbar_brand_html = page.locator('.navbar-brand').inner_html()
            print(navbar_brand_html)
            
            # 检查页面源代码中是否包含logo
            print("\n📋 检查页面源代码...")
            page_content = page.content()
            if 'images/logo.png' in page_content:
                print("✅ 页面源代码中找到logo路径")
            else:
                print("❌ 页面源代码中未找到logo路径")
                
            if 'static' in page_content:
                print("✅ 页面中包含static标签")
            else:
                print("❌ 页面中不包含static标签")
            
            # 检查所有img标签
            print("\n📋 页面中所有img标签:")
            img_elements = page.locator('img').all()
            for i, img in enumerate(img_elements):
                src = img.get_attribute('src')
                alt = img.get_attribute('alt')
                print(f"  img[{i}]: src='{src}', alt='{alt}'")
            
            # 尝试直接访问logo文件
            print("\n🔍 测试logo文件访问...")
            logo_urls = [
                'http://127.0.0.1:8000/static/images/logo.png',
                'http://127.0.0.1:8000/staticfiles/images/logo.png'
            ]
            
            for url in logo_urls:
                try:
                    response = page.goto(url)
                    if response.status == 200:
                        print(f"✅ Logo文件可访问: {url}")
                    else:
                        print(f"❌ Logo文件访问失败: {url} (状态: {response.status})")
                except Exception as e:
                    print(f"❌ Logo文件访问异常: {url} - {e}")
                    
                # 返回首页继续测试
                page.goto('http://127.0.0.1:8000/')
                time.sleep(1)
            
            # 检查Django设置
            print("\n🔍 检查Django静态文件设置...")
            page.goto('http://127.0.0.1:8000/admin/')
            time.sleep(2)
            
            # 截图保存
            screenshot_path = 'tests/ui/screenshots/logo_debug.png'
            page.goto('http://127.0.0.1:8000/')
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"📸 调试截图已保存: {screenshot_path}")
            
        except Exception as e:
            print(f"❌ 调试失败: {e}")
            
        finally:
            browser.close()

if __name__ == "__main__":
    debug_logo_issue()
