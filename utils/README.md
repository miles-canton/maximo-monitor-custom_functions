# Utils 工具文件夹

本文件夹包含 Maximo Monitor 自定义函数开发的实用工具脚本。

## 文件说明

### 1. db2_utils.py
**用途**: DB2 数据库连接工具模块

**功能**:
- `setup_ssl_no_verify()` - 禁用 SSL 证书验证（用于开发/测试环境）
- `setup_db2_connection_logger()` - 启用 DB2 连接字符串日志记录

**使用方法**:
```python
from utils.db2_utils import setup_ssl_no_verify, setup_db2_connection_logger

setup_ssl_no_verify()
setup_db2_connection_logger()
```

---

### 2. unregister_function.py
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

### 3. list_registered_functions.py
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
- [IBM Maximo Monitor 文档](https://www.ibm.com/docs/en/maximo-monitor)
- [IBM Watson IoT Functions GitHub](https://github.com/ibm-watson-iot/functions)