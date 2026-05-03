import json
import logging
import urllib3
import ssl
import inspect

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Monkey patch urllib3 to disable SSL verification globally
original_poolmanager_init = urllib3.PoolManager.__init__

def patched_poolmanager_init(self, *args, **kwargs):
    kwargs['cert_reqs'] = ssl.CERT_NONE
    kwargs['assert_hostname'] = False
    return original_poolmanager_init(self, *args, **kwargs)

urllib3.PoolManager.__init__ = patched_poolmanager_init

# Fix for Python 3.11: getargspec was removed, use getfullargspec instead
if not hasattr(inspect, 'getargspec'):
    inspect.getargspec = inspect.getfullargspec

from iotfunctions.db import Database
from iotfunctions.enginelog import EngineLogging

EngineLogging.configure_console_logging(logging.DEBUG)

with open('credentials_as_dev.json', encoding='utf-8') as F:
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
