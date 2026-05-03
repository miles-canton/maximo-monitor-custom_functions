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

'''
You can test functions locally before registering them on the server to
understand how they work.

Supply credentials by pasting them from the usage section into the UI.
Place your credentials in a separate file that you don't check into the repo. 

'''

with open('credentials_as.json', encoding='utf-8') as F:
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
# import the CLASS HelloWorld_MJ from custom_MJ.functions to be tested
from custom_MJ.functions import HelloWorld_MJ

fn = HelloWorld_MJ(name='AS_Tester', greeting_col='greeting')
fn.execute_local_test(db=db, db_schema=db_schema)

'''
Register function so that you can see it in the UI
'''

db.register_functions([HelloWorld_MJ])

# Made with Bob
