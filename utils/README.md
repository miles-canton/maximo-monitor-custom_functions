# Utils 工具文件夹

本文件夹包含 Maximo Monitor 自定义函数开发的实用工具脚本。

## 文件说明

### 1. db2_utils.py
**用途**: DB2 数据库连接工具模块（含自动证书更新功能）

**核心功能**:
- `quick_setup(credentials)` - **一键设置函数（推荐）**
  - 自动禁用 SSL 证书验证（开发/测试环境）
  - 自动下载最新的 DB2 SSL 证书
  - 自动配置 DB2 连接日志记录器
  
- `setup_all(db2_host, db2_port, cert_file, force_download_cert)` - 完整设置函数
  - 支持自定义 DB2 主机和端口
  - 支持自定义证书文件路径
  - 支持强制下载或使用现有证书
  
- `download_db2_certificate(db2_host, db2_port, cert_file)` - 下载 DB2 SSL 证书
  - 从 DB2 服务器下载最新的 SSL 证书
  - 自动保存到指定文件
  - 返回下载是否成功

- `setup_ssl_no_verify()` - 禁用 SSL 证书验证（用于开发/测试环境）
- `setup_db2_connection_logger()` - 启用 DB2 连接字符串日志记录

**使用方法**:

**方法 1: 一键设置（推荐）**
```python
from utils.db2_utils import quick_setup

# 一键设置：SSL 禁用 + 证书下载 + 日志配置
quick_setup(credentials)

# 然后正常使用数据库连接
from iotfunctions.db import Database
db = Database(credentials=credentials)
```

**方法 2: 完整设置**
```python
from utils.db2_utils import setup_all

# 完整设置，支持自定义参数
setup_all(
    db2_host="your-db2-host.com",
    db2_port=443,
    cert_file="db2_certificate.pem",
    force_download_cert=True  # 默认为 True，每次都下载最新证书
)
```

**方法 3: 单独使用各个函数**
```python
from utils.db2_utils import (
    setup_ssl_no_verify,
    setup_db2_connection_logger,
    download_db2_certificate
)

# 禁用 SSL 验证
setup_ssl_no_verify()

# 下载最新证书
download_db2_certificate(
    db2_host="your-db2-host.com",
    db2_port=443,
    cert_file="db2_certificate.pem"
)

# 启用日志
setup_db2_connection_logger()
```

**证书自动更新特性**:
- ✅ 默认每次运行都下载最新证书（`force_download_cert=True`）
- ✅ 如果下载失败，自动回退使用现有证书
- ✅ 证书文件保存为 `db2_certificate.pem`（默认）
- ✅ 支持自定义证书文件路径
- ✅ 证书大小约 3059 字节

---

### 2. function_utils.py
**用途**: 函数管理工具模块（Python SDK 方式）

**核心功能**:
- `get_registered_functions(db, custom_only=False)` - 获取已注册函数列表
  - 支持 `custom_only` 参数，只获取自定义函数
  - 返回包含 `catalogFunctionId` 的函数列表
  
- `is_function_registered(db, function_name)` - 检查函数是否已注册
  - 快速检查函数是否存在
  - 返回布尔值
  
- `unregister_function(db, function_name_or_id)` - 注销指定函数
  - 支持使用函数名或 `catalogFunctionId`
  - **推荐使用 catalogFunctionId 进行精确操作**
  
- `safe_unregister_function(db, function_name)` - 安全地注销函数
  - 先检查函数是否存在，再删除
  - 返回 (success, message) 元组
  - **推荐在测试脚本中使用**

**使用方法**:

**示例 1: 获取函数列表**
```python
from utils.function_utils import get_registered_functions

# 获取所有已注册的函数
all_functions = get_registered_functions(db)
print(f"找到 {len(all_functions)} 个函数")

# 只获取自定义函数
custom_functions = get_registered_functions(db, custom_only=True)
print(f"找到 {len(custom_functions)} 个自定义函数")

# 显示函数的 catalogFunctionId
for func in custom_functions:
    print(f"  - {func['name']} (catalogFunctionId: {func['catalogFunctionId']})")
```

**示例 2: 检查函数是否已注册**
```python
from utils.function_utils import is_function_registered

# 检查函数是否已注册
if is_function_registered(db, 'MyFunction'):
    print("函数已存在")
else:
    print("函数未注册")
```

**示例 3: 安全地删除函数（推荐）**
```python
from utils.function_utils import safe_unregister_function

# 安全地删除函数（先检查再删除）
success, message = safe_unregister_function(db, 'MyFunction')
print(message)
```

**示例 4: 直接删除函数**
```python
from utils.function_utils import unregister_function

# 使用函数名删除
unregister_function(db, 'MyFunction')

# 使用 catalogFunctionId 删除（推荐）
unregister_function(db, '128')
```

**示例 5: 在测试脚本中集成**
```python
from utils.function_utils import safe_unregister_function

# 在注册前安全地删除旧版本
print(f"\n🔍 检查函数 '{FUNCTION_NAME}' 是否已注册...")
success, message = safe_unregister_function(db, FUNCTION_NAME)
print(message)

# 注册新版本
db.register_functions([FUNCTION_CLASS])
```

**示例 6: 批量删除自定义函数**
```python
from utils.function_utils import get_registered_functions, unregister_function

# 获取所有自定义函数
custom_functions = get_registered_functions(db, custom_only=True)

# 删除所有自定义函数（使用 catalogFunctionId）
for func in custom_functions:
    catalog_id = func['catalogFunctionId']
    print(f"删除函数: {func['name']} (ID: {catalog_id})")
    unregister_function(db, catalog_id)
```

**优势**:
- ✅ 使用 Python SDK，无需手动构建 HTTP 请求
- ✅ 自动处理 API 凭证和认证
- ✅ 支持 `custom_only` 参数，只获取自定义函数
- ✅ 提供安全删除功能，避免误删
- ✅ 支持使用 catalogFunctionId 进行精确操作
- ✅ 返回包含 catalogFunctionId 的完整函数信息

---

### 3. unregister_function.py
**用途**: 注销已注册的函数

**功能**:
- 从 Maximo Monitor 服务器注销指定的自定义函数
- 允许重新注册同名函数

**使用方法**:
```bash
# 从项目根目录运行
wsl uv run python utils/unregister_function.py
```

**配置**:
编辑脚本中的 `function_name` 变量来指定要注销的函数名：
```python
function_name = 'YourFunctionName'
```

---

### 4. list_registered_functions.py
**用途**: 查询已注册的函数列表

**功能**:
- 列出所有已注册的函数（内置函数和自定义函数）
- 显示函数的详细信息（名称、分类、模块、描述）
- 加载函数目录

**使用方法**:
```bash
# 从项目根目录运行
wsl uv run python utils/list_registered_functions.py
```

**输出示例**:
```
✅ 找到 105 个已注册的函数

1. ActivityDuration
   分类: TRANSFORMER
   模块: iotfunctions.bif.ActivityDuration
   描述: 合并包含活动的多个表中的数据

2. AlertExpression
   分类: ALERT
   模块: iotfunctions.bif.AlertExpression
   描述: 当数据值达到特定范围时触发警报
...
```

---

## 使用注意事项

### 凭证文件
所有工具脚本都会尝试读取凭证文件，优先级如下：
1. `credentials_as_dev.json` (推荐 - 已在 .gitignore 中)
2. `credentials_as.json` (模板文件)

### 运行位置
- 所有脚本都应该从**项目根目录**运行
- 脚本会自动处理相对路径

### Python 环境
确保在正确的虚拟环境中运行：
```bash
# 使用 uv 运行
wsl uv run python utils/script_name.py

# 或激活虚拟环境后运行
wsl source .venv/bin/activate
wsl python utils/script_name.py
```

---

## 常见问题

### Q: 为什么需要禁用 SSL 验证？
A: 在开发/测试环境中，某些 DB2 实例可能使用自签名证书。禁用 SSL 验证可以避免证书验证错误。**生产环境中不应禁用 SSL 验证**。

### Q: 如何查看特定函数的详细信息？
A: 运行 `list_registered_functions.py` 后，在输出中搜索函数名称。

### Q: 注销函数失败怎么办？
A: 检查以下几点：
1. 函数名称是否正确
2. 凭证是否有效
3. 网络连接是否正常
4. API 权限是否足够

---

## 开发新工具

如果需要添加新的工具脚本，请遵循以下规范：

1. **导入 db2_utils**:
```python
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.db2_utils import setup_ssl_no_verify, setup_db2_connection_logger
```

2. **读取凭证文件**:
```python
credentials_file = '../credentials_as_dev.json'
if not os.path.exists(credentials_file):
    credentials_file = '../credentials_as.json'

with open(credentials_file, encoding='utf-8') as F:
    credentials = json.loads(F.read())
```

3. **添加文档**: 在本 README 中添加新工具的说明

---

## 相关文档

- [项目主 README](../README.md)
- [REST API 使用指南](./REST_API_GUIDE.md) - 详细的 HTTP REST API 使用说明
- [IBM Maximo Monitor 文档](https://www.ibm.com/docs/en/maximo-monitor)
- [IBM Watson IoT Functions GitHub](https://github.com/ibm-watson-iot/functions)