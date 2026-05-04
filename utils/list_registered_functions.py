#!/usr/bin/env python
"""查询 Maximo Monitor 中已注册的函数列表"""

import json
import logging
import sys
import os

# 添加父目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db2_utils import setup_ssl_no_verify, setup_db2_connection_logger

# 设置 SSL 禁用验证
setup_ssl_no_verify()
setup_db2_connection_logger()

from iotfunctions.db import Database
from iotfunctions.enginelog import EngineLogging

EngineLogging.configure_console_logging(logging.INFO)

# 加载凭证
try:
    with open('credentials_as_dev.json', encoding='utf-8') as F:
        credentials = json.loads(F.read())
except FileNotFoundError:
    print("❌ 未找到 credentials_as_dev.json，尝试使用 credentials_as.json")
    with open('credentials_as.json', encoding='utf-8') as F:
        credentials = json.loads(F.read())

# 创建数据库连接
db = Database(credentials=credentials)

print("=" * 80)
print("查询已注册的函数列表")
print("=" * 80)
print()

# 方法 1: 使用 http_request 获取所有函数
print("方法 1: 使用 http_request API 查询")
print("-" * 80)
try:
    response = db.http_request(
        object_type='allFunctions',
        object_name='',
        request='GET',
        raise_error=True
    )
    
    if response:
        print(f"✅ 响应类型: {type(response)}")
        print(f"✅ 响应长度: {len(response) if hasattr(response, '__len__') else 'N/A'}")
        
        # 如果响应是字符串，尝试解析为 JSON
        if isinstance(response, str):
            try:
                functions = json.loads(response)
            except:
                print(f"⚠️  响应内容（前500字符）: {response[:500]}")
                functions = []
        elif isinstance(response, list):
            functions = response
        elif isinstance(response, dict):
            functions = [response]
        else:
            functions = []
        
        if functions and isinstance(functions, list):
            print(f"✅ 找到 {len(functions)} 个已注册的函数\n")
            
            # 显示前20个函数
            for i, func in enumerate(functions[:20], 1):
                if isinstance(func, dict):
                    name = func.get('name', 'N/A')
                    category = func.get('category', 'N/A')
                    description = func.get('description', 'N/A')
                    module = func.get('moduleAndTargetName', 'N/A')
                    
                    print(f"{i}. {name}")
                    print(f"   分类: {category}")
                    print(f"   模块: {module}")
                    print(f"   描述: {description[:100]}..." if len(description) > 100 else f"   描述: {description}")
                    print()
                else:
                    print(f"{i}. {func}")
            
            if len(functions) > 20:
                print(f"... 还有 {len(functions) - 20} 个函数未显示")
        else:
            print("⚠️  未找到已注册的函数或响应格式不正确")
        
except Exception as e:
    print(f"❌ 查询失败: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 80)

# 方法 2: 使用 load_catalog 加载函数目录
print("方法 2: 使用 load_catalog 加载函数目录")
print("-" * 80)
try:
    catalog = db.load_catalog(install_missing=False)
    
    if catalog:
        print(f"✅ 目录中有 {len(catalog)} 个函数\n")
        
        # 显示函数名称列表
        function_names = sorted(catalog.keys())
        for i, name in enumerate(function_names, 1):
            func_class = catalog[name]
            print(f"{i:3d}. {name:50s} ({func_class.__module__})")
    else:
        print("⚠️  目录为空")
        
except Exception as e:
    print(f"❌ 加载目录失败: {e}")

print()
print("=" * 80)

# 方法 3: 查询特定函数的详细信息（使用 kpiFunctions）
print("方法 3: 查询实体类型的函数")
print("-" * 80)

try:
    # 尝试获取 kpiFunctions
    response = db.http_request(
        object_type='kpiFunctions',
        object_name='',
        request='GET',
        raise_error=False
    )
    
    if response:
        print(f"✅ 响应类型: {type(response)}")
        if isinstance(response, str):
            print(f"响应内容（前500字符）: {response[:500]}")
        elif isinstance(response, (list, dict)):
            print(json.dumps(response, indent=2, ensure_ascii=False)[:1000])
    else:
        print(f"⚠️  未获取到 kpiFunctions")
        
except Exception as e:
    print(f"❌ 查询失败: {e}")

print()
print("=" * 80)
print("查询完成")
print("=" * 80)

# Made with Bob
