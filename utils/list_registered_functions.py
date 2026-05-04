#!/usr/bin/env python
"""查询 Maximo Monitor 中已注册的函数列表"""

import json
import logging
import sys
import os
import argparse
import requests

# 添加父目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db2_utils import setup_ssl_no_verify

# 设置 SSL 禁用验证
setup_ssl_no_verify()

# 解析命令行参数
parser = argparse.ArgumentParser(description='查询 Maximo Monitor 中已注册的函数列表')
parser.add_argument('--custom-only', action='store_true',
                    help='只列出自定义函数')
parser.add_argument('--show-catalog-id', action='store_true',
                    help='显示 catalogFunctionId')
args = parser.parse_args()

# 加载凭证
try:
    with open('credentials_as_dev.json', encoding='utf-8') as F:
        credentials = json.loads(F.read())
except FileNotFoundError:
    print("❌ 未找到 credentials_as_dev.json，尝试使用 credentials_as.json")
    with open('credentials_as.json', encoding='utf-8') as F:
        credentials = json.loads(F.read())

# 提取 API 信息
tenant_id = credentials['tenantId']
api_key = credentials['iotp']['apiKey']
api_token = credentials['iotp']['apiToken']
as_host = credentials['iotp']['asHost']

print("=" * 80)
if args.custom_only:
    print("查询已注册的自定义函数列表")
else:
    print("查询已注册的函数列表")
print("=" * 80)
print()

# 使用 REST API 直接获取函数
try:
    # 构建 URL
    base_url = f"https://{as_host}/api/catalog/v1/{tenant_id}/function"
    params = {'customFunctionsOnly': 'true'} if args.custom_only else {'customFunctionsOnly': 'false'}
    
    # 设置请求头
    headers = {
        'X-api-key': api_key,
        'X-api-token': api_token
    }
    
    # 发送请求
    response = requests.get(base_url, params=params, headers=headers, verify=False)
    response.raise_for_status()
    
    functions = response.json()
    
    if functions and isinstance(functions, list):
        if args.custom_only:
            print(f"✅ 找到 {len(functions)} 个自定义函数\n")
        else:
            print(f"✅ 找到 {len(functions)} 个已注册的函数\n")
        
        # 分类统计
        if not args.custom_only:
            custom_count = sum(1 for f in functions if isinstance(f, dict) and 'custom' in f.get('moduleAndTargetName', '').lower())
            system_count = len(functions) - custom_count
            print(f"📊 统计: 系统函数 {system_count} 个, 自定义函数 {custom_count} 个\n")
        
        # 显示所有函数
        for i, func in enumerate(functions, 1):
            if isinstance(func, dict):
                name = func.get('name', 'N/A')
                category = func.get('category', 'N/A')
                description = func.get('description', 'N/A')
                module = func.get('moduleAndTargetName', 'N/A')
                catalog_id = func.get('catalogFunctionId', 'N/A')
                
                print(f"{i}. {name}")
                if args.show_catalog_id:
                    print(f"   catalogFunctionId: {catalog_id}")
                print(f"   分类: {category}")
                print(f"   模块: {module}")
                
                # 只在非自定义模式下显示描述（避免输出过长）
                if not args.custom_only:
                    print(f"   描述: {description[:100]}..." if len(description) > 100 else f"   描述: {description}")
                print()
            else:
                print(f"{i}. {func}")
    else:
        print("⚠️  未找到已注册的函数或响应格式不正确")
        
except Exception as e:
    print(f"❌ 查询失败: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 80)
print("查询完成")
print("=" * 80)

# Made with Bob
