#!/usr/bin/env python3
"""
自动截图脚本
使用Playwright自动访问系统并截图

使用方式：
1. 打开系统URL
2. 处理登录（cookie或自动登录）
3. 按功能模块导航到各个页面
4. 截图并命名

依赖：
- playwright
- asyncio
"""

import os
import json
import asyncio
import argparse
from pathlib import Path
from typing import Dict, List, Optional


async def setup_browser(headless: bool = True):
    """
    设置浏览器
    
    Args:
        headless: 是否无头模式
        
    Returns:
        browser, context, page
    """
    from playwright.async_api import async_playwright
    
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=headless)
    context = await browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        locale='zh-CN'
    )
    page = await context.new_page()
    
    return playwright, browser, context, page


async def login_with_cookie(page, url: str, cookies: List[Dict]):
    """
    使用cookie登录
    
    Args:
        page: Playwright page对象
        url: 系统URL
        cookies: cookie列表 [{"name": str, "value": str, "domain": str}]
    """
    # 先访问域名以设置cookie
    await page.goto(url)
    
    # 设置cookie
    for cookie in cookies:
        if 'domain' not in cookie:
            # 从URL提取domain
            from urllib.parse import urlparse
            parsed = urlparse(url)
            cookie['domain'] = parsed.hostname
        
        await page.context.add_cookies([cookie])
    
    # 刷新页面使cookie生效
    await page.reload()
    await page.wait_for_load_state('networkidle')
    
    print(f"已设置 {len(cookies)} 个cookie")


async def login_with_credentials(page, url: str, username: str, password: str, 
                                  username_selector: str = 'input[name="username"]',
                                  password_selector: str = 'input[name="password"]',
                                  submit_selector: str = 'button[type="submit"]'):
    """
    使用账号密码登录
    
    Args:
        page: Playwright page对象
        url: 系统URL
        username: 用户名
        password: 密码
        username_selector: 用户名输入框选择器
        password_selector: 密码输入框选择器
        submit_selector: 提交按钮选择器
    """
    await page.goto(url)
    await page.wait_for_load_state('networkidle')
    
    # 填写用户名
    await page.fill(username_selector, username)
    
    # 填写密码
    await page.fill(password_selector, password)
    
    # 点击登录按钮
    await page.click(submit_selector)
    
    # 等待登录完成
    await page.wait_for_load_state('networkidle')
    await asyncio.sleep(2)  # 额外等待
    
    print("登录成功")


async def take_screenshot(page, output_path: str, 
                           full_page: bool = False,
                           clip: Optional[Dict] = None):
    """
    截图
    
    Args:
        page: Playwright page对象
        output_path: 输出路径
        full_page: 是否全页截图
        clip: 裁剪区域 {"x": int, "y": int, "width": int, "height": int}
    """
    await page.screenshot(
        path=output_path,
        full_page=full_page,
        clip=clip
    )
    print(f"截图已保存：{output_path}")


async def navigate_and_screenshot(page, url: str, screenshot_name: str,
                                    output_dir: str, wait_time: float = 2.0):
    """
    导航到URL并截图
    
    Args:
        page: Playwright page对象
        url: 目标URL
        screenshot_name: 截图文件名
        output_dir: 输出目录
        wait_time: 等待时间（秒）
    """
    await page.goto(url)
    await page.wait_for_load_state('networkidle')
    await asyncio.sleep(wait_time)
    
    output_path = os.path.join(output_dir, screenshot_name)
    await take_screenshot(page, output_path)


async def auto_screenshot_by_modules(page, base_url: str, modules: List[Dict],
                                       output_dir: str):
    """
    按功能模块自动截图
    
    Args:
        page: Playwright page对象
        base_url: 基础URL
        modules: 功能模块列表 [{"name": str, "path": str, "description": str}]
        output_dir: 输出目录
    """
    os.makedirs(output_dir, exist_ok=True)
    
    screenshots = []
    
    for i, module in enumerate(modules, 1):
        module_name = module.get('name', f'模块{i}')
        module_path = module.get('path', '')
        description = module.get('description', '')
        
        # 构建完整URL
        if module_path.startswith('http'):
            url = module_path
        else:
            url = f"{base_url.rstrip('/')}/{module_path.lstrip('/')}"
        
        # 截图文件名
        screenshot_name = f"{i:02d}_{module_name}.png"
        
        try:
            await navigate_and_screenshot(page, url, screenshot_name, output_dir)
            
            screenshots.append({
                "name": screenshot_name,
                "module": module_name,
                "description": description,
                "url": url,
                "status": "success"
            })
        except Exception as e:
            print(f"截图失败 {module_name}: {e}")
            screenshots.append({
                "name": screenshot_name,
                "module": module_name,
                "description": description,
                "url": url,
                "status": "failed",
                "error": str(e)
            })
    
    return screenshots


async def auto_screenshot_interactive(page, base_url: str, output_dir: str,
                                        manual_content: Dict):
    """
    交互式自动截图
    根据说明书内容自动导航到相关页面并截图
    
    Args:
        page: Playwright page对象
        base_url: 基础URL
        output_dir: 输出目录
        manual_content: 说明书内容JSON
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # 从说明书内容中提取需要截图的功能
    features = extract_features_for_screenshot(manual_content)
    
    screenshots = []
    
    for i, feature in enumerate(features, 1):
        feature_name = feature.get('name', f'功能{i}')
        feature_path = feature.get('path', '')
        description = feature.get('description', '')
        
        if not feature_path:
            print(f"跳过 {feature_name}：没有URL路径")
            continue
        
        # 构建完整URL
        if feature_path.startswith('http'):
            url = feature_path
        else:
            url = f"{base_url.rstrip('/')}/{feature_path.lstrip('/')}"
        
        # 截图文件名
        screenshot_name = f"{i:02d}_{feature_name}.png"
        
        try:
            await navigate_and_screenshot(page, url, screenshot_name, output_dir)
            
            screenshots.append({
                "name": screenshot_name,
                "feature": feature_name,
                "description": description,
                "url": url,
                "status": "success"
            })
        except Exception as e:
            print(f"截图失败 {feature_name}: {e}")
            screenshots.append({
                "name": screenshot_name,
                "feature": feature_name,
                "description": description,
                "url": url,
                "status": "failed",
                "error": str(e)
            })
    
    return screenshots


def extract_features_for_screenshot(manual_content: Dict) -> List[Dict]:
    """
    从说明书内容中提取需要截图的功能
    
    Args:
        manual_content: 说明书内容JSON
        
    Returns:
        功能列表 [{"name": str, "path": str, "description": str}]
    """
    features = []
    
    def extract_from_dict(content, path=""):
        for key, value in content.items():
            if isinstance(value, str):
                # 检查是否需要截图
                if "[截图:" in value or "如下图" in value:
                    # 尝试从key或value中提取URL路径
                    url_path = extract_url_path(key, value)
                    features.append({
                        "name": key,
                        "path": url_path,
                        "description": value
                    })
            elif isinstance(value, dict):
                extract_from_dict(value, f"{path}/{key}" if path else key)
    
    extract_from_dict(manual_content)
    return features


def extract_url_path(key: str, description: str) -> str:
    """
    从标题或描述中提取URL路径
    
    Args:
        key: 标题
        description: 描述
        
    Returns:
        URL路径
    """
    # 简单的路径推断逻辑
    # 实际使用时可能需要更复杂的映射
    
    path_mapping = {
        "登录": "/login",
        "首页": "/",
        "主页": "/",
        "用户管理": "/admin/users",
        "数据管理": "/data",
        "系统设置": "/settings",
        "查询": "/search",
        "列表": "/list"
    }
    
    for keyword, path in path_mapping.items():
        if keyword in key or keyword in description:
            return path
    
    return ""


async def main_async(args):
    """异步主函数"""
    playwright, browser, context, page = await setup_browser(headless=not args.visible)
    
    try:
        # 处理登录
        if args.cookie:
            # 使用cookie登录
            with open(args.cookie, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            await login_with_cookie(page, args.url, cookies)
        elif args.username and args.password:
            # 使用账号密码登录
            await login_with_credentials(
                page, args.url, args.username, args.password,
                args.username_selector, args.password_selector, args.submit_selector
            )
        
        # 截图模式
        if args.modules:
            # 按模块截图
            with open(args.modules, 'r', encoding='utf-8') as f:
                modules = json.load(f)
            screenshots = await auto_screenshot_by_modules(
                page, args.url, modules, args.output
            )
        elif args.manual:
            # 根据说明书自动截图
            with open(args.manual, 'r', encoding='utf-8') as f:
                manual_content = json.load(f)
            screenshots = await auto_screenshot_interactive(
                page, args.url, args.output, manual_content
            )
        else:
            # 单页截图
            screenshots = []
            output_path = os.path.join(args.output, "screenshot.png")
            await take_screenshot(page, output_path, full_page=args.full_page)
            screenshots.append({
                "name": "screenshot.png",
                "url": args.url,
                "status": "success"
            })
        
        # 保存截图结果
        result_path = os.path.join(args.output, "screenshot_results.json")
        with open(result_path, 'w', encoding='utf-8') as f:
            json.dump(screenshots, f, ensure_ascii=False, indent=2)
        
        print(f"\n截图完成！共 {len(screenshots)} 张")
        print(f"结果保存到：{result_path}")
        
    finally:
        await browser.close()
        await playwright.stop()


def main():
    parser = argparse.ArgumentParser(description='自动截图工具')
    parser.add_argument('--url', required=True, help='系统URL')
    parser.add_argument('--output', required=True, help='输出目录')
    
    # 登录方式
    login_group = parser.add_argument_group('登录选项')
    login_group.add_argument('--cookie', help='cookie JSON文件路径')
    login_group.add_argument('--username', help='用户名')
    login_group.add_argument('--password', help='密码')
    login_group.add_argument('--username-selector', default='input[name="username"]', 
                            help='用户名输入框选择器')
    login_group.add_argument('--password-selector', default='input[name="password"]',
                            help='密码输入框选择器')
    login_group.add_argument('--submit-selector', default='button[type="submit"]',
                            help='提交按钮选择器')
    
    # 截图选项
    screenshot_group = parser.add_argument_group('截图选项')
    screenshot_group.add_argument('--modules', help='功能模块JSON文件')
    screenshot_group.add_argument('--manual', help='说明书内容JSON文件')
    screenshot_group.add_argument('--full-page', action='store_true', help='全页截图')
    screenshot_group.add_argument('--visible', action='store_true', help='显示浏览器窗口')
    
    args = parser.parse_args()
    
    # 运行异步主函数
    asyncio.run(main_async(args))


if __name__ == '__main__':
    main()
