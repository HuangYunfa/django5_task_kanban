#!/usr/bin/env python3
"""
Logo显示测试 - 检查导航栏logo是否正确显示
"""

import time
import sys
import os
from playwright.sync_api import sync_playwright

def test_logo_display():
    """测试logo在导航栏中的显示"""
    
    with sync_playwright() as p:
        # 启动浏览器 - 可见模式便于调试
        browser = p.chromium.launch(headless=False, slow_mo=1000)
        context = browser.new_context(viewport={'width': 1280, 'height': 720})
        page = context.new_page()
        
        try:
            print("🔍 开始测试logo显示...")
            
            # 访问首页
            print("📱 访问首页...")
            page.goto('http://127.0.0.1:8000/')
            page.wait_for_load_state('networkidle', timeout=10000)
            time.sleep(2)
            
            # 检查logo元素是否存在
            print("🎨 检查logo元素...")
            logo_selector = 'img[alt="Logo"]'
            
            if page.locator(logo_selector).count() > 0:
                print("✅ Logo元素找到！")
                
                # 获取logo元素信息
                logo_element = page.locator(logo_selector).first
                
                # 检查logo是否可见
                if logo_element.is_visible():
                    print("✅ Logo可见！")
                    
                    # 获取logo属性
                    src = logo_element.get_attribute('src')
                    width = logo_element.get_attribute('width')
                    height = logo_element.get_attribute('height')
                    
                    print(f"📋 Logo信息:")
                    print(f"   - 源文件: {src}")
                    print(f"   - 宽度: {width}px")
                    print(f"   - 高度: {height}px")
                    
                    # 检查logo是否加载成功（检查naturalWidth）
                    natural_width = page.evaluate('''
                        () => {
                            const img = document.querySelector('img[alt="Logo"]');
                            return img ? img.naturalWidth : 0;
                        }
                    ''')
                    
                    if natural_width > 0:
                        print(f"✅ Logo图片加载成功！实际宽度: {natural_width}px")
                    else:
                        print("❌ Logo图片加载失败！")
                        
                        # 检查图片加载错误
                        page.evaluate('''
                            () => {
                                const img = document.querySelector('img[alt="Logo"]');
                                if (img) {
                                    img.onerror = () => console.log('Logo加载错误:', img.src);
                                }
                            }
                        ''')
                else:
                    print("❌ Logo不可见！")
            else:
                print("❌ 未找到Logo元素！")
                
            # 检查navbar-brand结构
            print("\n🔍 检查navbar-brand结构...")
            navbar_brand = page.locator('.navbar-brand')
            if navbar_brand.count() > 0:
                print("✅ 找到navbar-brand")
                brand_html = navbar_brand.inner_html()
                print(f"📋 navbar-brand内容: {brand_html}")
            else:
                print("❌ 未找到navbar-brand！")
            
            # 截图保存
            screenshot_path = 'tests/ui/screenshots/logo_test.png'
            os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"📸 截图已保存: {screenshot_path}")
            
            # 检查控制台错误
            print("\n🔍 检查控制台错误...")
            page.on('console', lambda msg: print(f"Console: {msg.type}: {msg.text}"))
            
            time.sleep(3)
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            return False
            
        finally:
            browser.close()
            
    return True

if __name__ == "__main__":
    print("🚀 启动Logo显示测试...")
    
    # 确保Django服务器运行
    print("⚠️  请确保Django服务器正在运行: python manage.py runserver")
    time.sleep(2)
    
    test_logo_display()
    print("✅ Logo测试完成！")
