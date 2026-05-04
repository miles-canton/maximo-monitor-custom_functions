#!/usr/bin/env python
"""函数管理工具模块"""

import json
import logging
import requests

logger = logging.getLogger(__name__)


def _get_api_info(db):
    """
    从 Database 实例中提取 API 信息
    
    Args:
        db: Database 实例
        
    Returns:
        tuple: (tenant_id, api_key, api_token, as_host)
    """
    # 从 db.credentials 字典中提取信息
    creds = db.credentials
    
    # 提取 tenant_id
    tenant_id = creds.get('tenant_id')
    
    # 从 'as' 子字典中提取 API 信息
    as_info = creds.get('as', {})
    api_key = as_info.get('api_key', '')
    api_token = as_info.get('api_token', '')
    as_host = as_info.get('host', '')
    
    return tenant_id, api_key, api_token, as_host


def is_function_registered(db, function_name):
    """
    检查函数是否已在 Maximo Monitor 中注册
    
    Args:
        db: Database 实例
        function_name: 函数名称
        
    Returns:
        bool: 如果函数已注册返回 True，否则返回 False
    """
    try:
        functions = get_registered_functions(db, custom_only=False)
        
        # 检查函数名是否在列表中
        for func in functions:
            if isinstance(func, dict) and func.get('name') == function_name:
                return True
        
        return False
        
    except Exception as e:
        logger.warning(f"检查函数是否注册时出错: {e}")
        return False


def get_registered_functions(db, custom_only=False):
    """
    获取已注册的函数列表
    
    Args:
        db: Database 实例
        custom_only: 是否只获取自定义函数 (default: False)
        
    Returns:
        list: 函数字典列表，每个字典包含 name, category, module, catalogFunctionId 等信息
        
    Example:
        # 获取所有函数
        all_functions = get_registered_functions(db)
        
        # 只获取自定义函数
        custom_functions = get_registered_functions(db, custom_only=True)
    """
    try:
        # 提取 API 信息
        tenant_id, api_key, api_token, as_host = _get_api_info(db)
        
        # 构建 URL 和参数
        base_url = f"https://{as_host}/api/catalog/v1/{tenant_id}/function"
        params = {'customFunctionsOnly': 'true' if custom_only else 'false'}
        
        # 设置请求头
        headers = {
            'X-api-key': api_key,
            'X-api-token': api_token
        }
        
        # 发送请求
        response = requests.get(base_url, params=params, headers=headers, verify=False)
        response.raise_for_status()
        
        functions = response.json()
        
        if isinstance(functions, list):
            return functions
        
        return []
        
    except Exception as e:
        logger.error(f"获取已注册函数列表失败: {e}")
        return []


def unregister_function(db, function_name_or_id):
    """
    注销指定的函数
    
    Args:
        db: Database 实例
        function_name_or_id: 要注销的函数名称或 catalogFunctionId
        
    Returns:
        bool: 成功返回 True，失败返回 False
        
    Example:
        # 使用函数名删除
        unregister_function(db, 'HelloWorld_MJ')
        
        # 使用 catalogFunctionId 删除（推荐）
        unregister_function(db, '128')
    """
    try:
        db.http_request(
            object_type='function',
            object_name=str(function_name_or_id),
            request='DELETE',
            payload={}
        )
        logger.info(f"✅ 成功注销函数: {function_name_or_id}")
        return True
        
    except Exception as e:
        logger.error(f"❌ 注销函数失败: {e}")
        return False


def safe_unregister_function(db, function_name):
    """
    安全地注销函数：先检查是否存在，存在才删除
    
    Args:
        db: Database 实例
        function_name: 要注销的函数名称
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # 先检查函数是否存在
    if is_function_registered(db, function_name):
        print(f"🔍 检测到函数 '{function_name}' 已注册，准备删除...")
        if unregister_function(db, function_name):
            return True, f"✅ 已删除旧版本的函数 '{function_name}'"
        else:
            return False, f"❌ 删除函数 '{function_name}' 失败"
    else:
        return True, f"ℹ️  函数 '{function_name}' 未注册，无需删除"


# Made with Bob