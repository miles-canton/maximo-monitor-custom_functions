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

import inspect

# Fix for Python 3.11: getargspec was removed, use getfullargspec instead
if not hasattr(inspect, 'getargspec'):
    inspect.getargspec = inspect.getfullargspec

from iotfunctions.db import Database
from iotfunctions.enginelog import EngineLogging

EngineLogging.configure_console_logging(logging.DEBUG)

# 尝试读取凭证文件（优先使用 dev 版本）
credentials_file = '../credentials_as_dev.json'
if not os.path.exists(credentials_file):
    credentials_file = '../credentials_as.json'

with open(credentials_file, encoding='utf-8') as F:
    credentials = json.loads(F.read())

db = Database(credentials=credentials)

# Function name to unregister
function_name = 'HelloWorld_MJ'

print(f"\n尝试注销函数: {function_name}")

try:
    # Try to delete the function using HTTP DELETE request
    response = db.http_request(
        object_type='function',
        object_name=function_name,
        request='DELETE',
        payload={}
    )
    print(f"✅ 函数 {function_name} 已成功注销")
    print(f"响应: {response}")
except Exception as e:
    print(f"❌ 注销失败: {e}")
    print("\n可用的方法:")
    print([method for method in dir(db) if not method.startswith('_')])

# Made with Bob
