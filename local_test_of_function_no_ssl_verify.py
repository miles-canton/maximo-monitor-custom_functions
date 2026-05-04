import json
import logging
import inspect

# 使用 db2_utils 模块进行 DB2 调试设置
from utils.db2_utils import setup_ssl_no_verify, setup_db2_connection_logger

# 设置 SSL 禁用验证
setup_ssl_no_verify()

# 设置 DB2 连接字符串日志记录器
setup_db2_connection_logger()

# Fix for Python 3.11: getargspec was removed, use getfullargspec instead
if not hasattr(inspect, 'getargspec'):
    inspect.getargspec = inspect.getfullargspec

from iotfunctions.db import Database
from iotfunctions.enginelog import EngineLogging

EngineLogging.configure_console_logging(logging.DEBUG)

'''
You can test functions locally before registering them on the server to
understand how they work.

Supply credentials by pasting them from the usage section into the UI.
Place your credentials in a separate file that you don't check into the repo. 

'''

with open('credentials_as_dev.json', encoding='utf-8') as F:
    credentials = json.loads(F.read())
db_schema = None
db = Database(credentials=credentials)

'''
Import and instantiate the functions to be tested 

The local test will generate data instead of using server data.
By default it will assume that the input data items are numeric.

Required data items will be inferred from the function inputs.

The function below executes an expression involving a column called x1
The local test function will generate data dataframe containing the column x1

By default test results are written to a file named df_test_entity_for_<function_name>
This file will be written to the working directory.

'''
# 导入自定义函数
try:
    from custom.functions import HelloWorld as FUNCTION_CLASS
except ImportError as e:
    print(f"❌ 导入函数失败: {e}")
    print("📋 排查步骤:")
    print("   1. 检查 custom/functions.py 文件是否存在")
    print("   2. 检查 custom/__init__.py 文件是否存在")
    print("   3. 检查 HelloWorld 类是否在 custom/functions.py 中定义")
    print("   4. 检查是否有语法错误: python -m py_compile custom/functions.py")
    raise

FUNCTION_NAME = FUNCTION_CLASS.__name__

fn = FUNCTION_CLASS(name='AS_Tester', greeting_col='greeting')
fn.execute_local_test(db=db, db_schema=db_schema)

'''
Register function so that you can see it in the UI
先尝试删除已存在的函数，然后再注册
'''

# 尝试删除已存在的函数
try:
    print(f"\n检查函数 '{FUNCTION_NAME}' 是否已存在...")
    db.http_request(
        object_type='function',
        object_name=FUNCTION_NAME,
        request='DELETE',
        payload={}
    )
    print(f"✅ 已删除旧版本的函数 '{FUNCTION_NAME}'")
except Exception as e:
    print(f"ℹ️  函数 '{FUNCTION_NAME}' 不存在或删除失败（这是正常的）: {str(e)[:100]}")

# 注册函数
print(f"\n注册函数 '{FUNCTION_NAME}'...")
try:
    db.register_functions([FUNCTION_CLASS])
    print(f"✅ 函数 '{FUNCTION_NAME}' 注册成功")
except Exception as e:
    print(f"❌ 函数注册失败: {e}")
    print("📋 可能的原因:")
    print("   1. 函数定义有误")
    print("   2. 网络连接问题")
    print("   3. API权限不足")
    raise

# Made with Bob
