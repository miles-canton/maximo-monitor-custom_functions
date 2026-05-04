# maximo-monitor-custom_functions

Maximo Monitor 自定义函数开发和测试项目

## 项目结构

```
.
├── custom/                                      # 自定义函数模块 (示例)
│   ├── __init__.py
│   └── functions.py                            # 自定义函数实现
├── custom_MJ/                                   # 自定义函数模块 (MJ 示例)
│   ├── __init__.py
│   └── functions.py                            # 自定义函数实现
├── utils/                                       # 工具脚本文件夹
│   ├── db2_utils.py                            # DB2 数据库工具函数（含自动证书更新）
│   ├── function_utils.py                       # 函数管理工具模块
│   ├── unregister_function.py                  # 函数注销工具
│   ├── list_registered_functions.py            # 查询已注册函数列表
│   └── README.md                               # 工具说明文档
├── credentials_as.json                          # 凭证模板 (测试脚本使用)
├── credentials_as_dev.json                      # 真实凭证备份 (gitignore)
├── local_test_of_function_no_ssl_verify.py      # 通用测试脚本 (含修复)
├── local_test_of_function_no_ssl_verify_MJ.py   # MJ 示例测试脚本
├── requirements.txt                             # Python 依赖包列表
├── .gitignore                                   # Git 忽略文件配置
└── README.md                                    # 本文档
```

## 环境设置

### 前置要求

- Python 3.11
- uv (Python 包管理工具)
- WSL (Windows Subsystem for Linux) - 推荐用于 Windows 用户

**重要提示**: 由于 Windows 上的 DB2 CLI 驱动程序兼容性问题,强烈建议在 WSL 环境中运行。

### 1. 创建虚拟环境 (WSL)

使用 uv 在 WSL 中创建 Python 3.11 虚拟环境:

```bash
wsl uv venv --python 3.11
```

这将创建一个 `.venv` 目录,包含 Python 3.11 虚拟环境。

### 2. 安装依赖包

使用 requirements.txt 一键安装所有依赖:

```bash
wsl uv pip install -r requirements.txt
```

**包含的主要组件**:
- IBM Watson IoT Functions SDK (iotfunctions 8.3.1)
- 数据库驱动 (ibm-db, psycopg2-binary)
- 数据处理库 (pandas, numpy, pyarrow)
- 机器学习库 (scikit-learn, scipy, statsmodels)
- SQLAlchemy 1.4.53 (兼容性版本)

### 3. 配置凭证

项目包含两个凭证文件:

- **`credentials_as.json`** - 凭证模板文件 (包含占位符)
- **`credentials_as_dev.json`** - 真实凭证文件 (已在 .gitignore 中排除)

#### 凭证文件说明

仓库中的 `credentials_as.json` 是一个**模板文件**,包含占位符而非真实凭证。

#### 首次设置

复制 `credentials_as.json` 为 `credentials_as_dev.json`,然后填入您的真实凭证:

```bash
# 复制凭证模板
wsl cp credentials_as.json credentials_as_dev.json
```

编辑 `credentials_as_dev.json`,填入您的真实数据库和 IoT 平台凭证:

```json
{
    "tenantId": "ws1",
    "db2": {
        "username": "db2inst1",
        "password": "YOUR_DB2_PASSWORD",
        "databaseName": "BLUDB",
        "port": 443,
        "httpsUrl": "jdbc:db2://mas-inst1-system-db2u.apps.itz-7l9v61.infra01-lb.dal14.techzone.ibm.com:443/BLUDB:sslConnection=true;",
        "host": "mas-inst1-system-db2u.apps.itz-7l9v61.infra01-lb.dal14.techzone.ibm.com",
        "security": "SSL",
        "certificate": "db2_certificate.pem"
    },
    "iotp": {
        "url": "https://ws1.messaging.iot.inst1.apps.itz-b912y0.infra01-lb.dal14.techzone.ibm.com/api/v0002",
        "orgId": "ws1",
        "host": "ws1.messaging.iot.inst1.apps.itz-b912y0.infra01-lb.dal14.techzone.ibm.com",
        "port": 443,
        "asHost": "ws1.api.monitor.inst1.apps.itz-7l9v61.infra01-lb.dal14.techzone.ibm.com",
        "apiKey": "YOUR_API_KEY",
        "apiToken": "YOUR_API_TOKEN"
    },
    "_verify_ssl": false
}
```

**字段说明**:
- `tenantId`: 租户 ID
- `db2.username`: DB2 数据库用户名
- `db2.password`: DB2 数据库密码 (需要替换 YOUR_DB2_PASSWORD)
- `db2.port`: 数据库端口 (443 用于 SSL 连接)
- `db2.security`: 安全连接类型 (SSL)
- `db2.certificate`: SSL 证书文件路径 (不要修改)
- `iotp.apiKey`: IoT 平台 API 密钥 (需要替换 YOUR_API_KEY)
- `iotp.apiToken`: IoT 平台 API 令牌 (需要替换 YOUR_API_TOKEN)
- `_verify_ssl`: 是否验证 SSL 证书 (false 用于开发/测试环境)

**重要提示**:
- ⚠️ `credentials_as.json` - 凭证模板文件,**不要直接修改此文件填写真实凭证**
- ✅ `credentials_as_dev.json` - 已在 .gitignore 中排除,可以安全地存储真实凭证
- 📝 测试脚本默认读取 `credentials_as_dev.json`,如果不存在则读取 `credentials_as.json`
- 🔒 提交代码前,请确保 `credentials_as.json` 中只包含占位符,不包含真实密钥

---

## 使用方案

### 方案概述

本项目提供四种主要使用方案：

1. **快速测试现有函数** - 直接运行示例函数进行测试
2. **开发新的自定义函数** - 创建并测试您自己的函数
3. **更新和重新部署函数** - 修改现有函数并重新注册
4. **函数管理和 REST API** - 使用工具脚本和 REST API 管理函数

---

### 方案 1: 快速测试现有函数

适用场景：验证环境配置、了解工作流程

#### 步骤 1: 准备凭证文件

```bash
# 复制凭证模板
wsl cp credentials_as.json credentials_as_dev.json

# 编辑 credentials_as_dev.json，填入真实凭证
# 使用您喜欢的编辑器，如 vim、nano 或 VSCode
```

#### 步骤 2: 运行测试脚本

```bash
# 运行测试并注册示例函数
wsl uv run python local_test_of_function_no_ssl_verify_MJ.py
```

**测试脚本会自动执行以下操作**：
1. ✅ 自动下载最新的 DB2 SSL 证书（3059 字节）
2. ✅ 禁用 SSL 证书验证（开发/测试环境）
3. ✅ 配置 DB2 连接日志记录器
4. ✅ 建立数据库连接
5. ✅ 生成测试数据
6. ✅ 执行自定义函数
7. ✅ 注册函数到服务器

#### 步骤 3: 验证结果

```bash
# 查看生成的测试文件
wsl ls -lh df_TEST_ENTITY_FOR_*.csv

# 查看测试数据（前10行）
wsl head -10 df_TEST_ENTITY_FOR_HELLOWORLD_MJ.csv
```

**预期输出**：
- ✅ DB2 证书自动下载成功（3059 字节）
- ✅ 数据库连接成功建立
- ✅ 生成 1,446 行测试数据
- ✅ 函数执行成功
- ✅ 函数注册成功 (HTTP 200)
- ✅ 生成 CSV 测试文件（116K 或 163K）

---

### 方案 2: 开发新的自定义函数

适用场景：创建全新的数据处理函数

#### 步骤 1: 创建函数模块

```bash
# 复制示例模块（XX 替换为您的名字或标识）
wsl cp -r custom custom_XX
```

#### 步骤 2: 编写函数代码

编辑 `custom_XX/functions.py`：

```python
from iotfunctions.base import BaseTransformer

class YourFunctionName_XX(BaseTransformer):
    """
    您的自定义函数描述
    """
    def __init__(self, input_param, output_col):
        super().__init__()
        self.input_param = input_param
        self.output_col = output_col
    
    def execute(self, df):
        """
        执行数据转换逻辑
        
        参数:
            df: pandas DataFrame，包含输入数据
        
        返回:
            df: 处理后的 DataFrame
        """
        # 您的业务逻辑
        df[self.output_col] = df['input_col'].apply(
            lambda x: x * self.input_param
        )
        return df
```

#### 步骤 3: 创建测试脚本

```bash
# 复制测试脚本模板
wsl cp local_test_of_function_no_ssl_verify_MJ.py local_test_of_function_no_ssl_verify_XX.py
```

编辑 `local_test_of_function_no_ssl_verify_XX.py`，修改以下内容：

**修改 1: 导入语句**
```python
# 修改前
from custom_MJ.functions import HelloWorld_MJ

# 修改后
from custom_XX.functions import YourFunctionName_XX
```

**修改 2: 函数实例化**
```python
# 修改前
fn = HelloWorld_MJ(
    name='AS_Tester',
    greeting_col='greeting'
)

# 修改后
fn = YourFunctionName_XX(
    input_param=10,
    output_col='result'
)
```

**修改 3: 函数注册**
```python
# 修改前
db.register_functions([HelloWorld_MJ])

# 修改后
db.register_functions([YourFunctionName_XX])
```

#### 步骤 4: 运行测试

```bash
# 执行测试脚本
wsl uv run python local_test_of_function_no_ssl_verify_XX.py
```

#### 步骤 5: 验证结果

```bash
# 查看生成的测试文件
wsl ls -lh df_TEST_ENTITY_FOR_YOURFUNCTIONNAME_XX.csv

# 检查输出数据
wsl head -20 df_TEST_ENTITY_FOR_YOURFUNCTIONNAME_XX.csv
```

---

### 方案 3: 更新和重新部署函数

适用场景：修改现有函数并重新注册到服务器

#### 步骤 1: 修改函数代码

编辑 `custom_XX/functions.py`，更新您的函数逻辑

#### 步骤 2: 注销旧版本函数

编辑 `utils/unregister_function.py`，设置要注销的函数名：

```python
# 修改函数名为您要注销的函数
function_name = 'YourFunctionName_XX'
```

运行注销脚本：

```bash
wsl uv run python utils/unregister_function.py
```

#### 步骤 3: 清理旧测试文件

```bash
# 删除旧的测试输出文件
wsl rm -f df_TEST_ENTITY_FOR_YOURFUNCTIONNAME_XX.csv
```

#### 步骤 4: 重新测试和注册

```bash
# 运行测试脚本，生成新的测试文件并注册函数
wsl uv run python local_test_of_function_no_ssl_verify_XX.py
```

#### 步骤 5: 验证更新

```bash
# 检查新生成的测试文件
wsl ls -lh df_TEST_ENTITY_FOR_YOURFUNCTIONNAME_XX.csv

# 验证输出数据是否符合预期
wsl head -20 df_TEST_ENTITY_FOR_YOURFUNCTIONNAME_XX.csv
```

---

### 测试脚本说明

项目包含以下测试脚本：

| 脚本名称 | 用途 | 说明 |
|---------|------|------|
| `local_test_of_function_no_ssl_verify_MJ.py` | 示例测试脚本 | 测试 HelloWorld_MJ 函数，使用 quick_setup() |
| `local_test_of_function_no_ssl_verify.py` | 通用测试脚本 | 可复制并修改用于测试自定义函数，使用 quick_setup() |
| `utils/db2_utils.py` | DB2 工具模块 | 提供 quick_setup()、SSL 配置、证书自动下载 |
| `utils/function_utils.py` | 函数管理工具模块 | 提供函数查询、注册、注销等功能 |
| `utils/unregister_function.py` | 函数注销工具 | 用于注销已注册的函数 |
| `utils/list_registered_functions.py` | 函数列表查询工具 | 查询所有已注册的函数 |

**测试脚本功能**：
1. ✅ 自动下载最新的 DB2 SSL 证书
2. ✅ 加载凭证配置
3. ✅ 禁用 SSL 证书验证（开发/测试环境）
4. ✅ 配置 DB2 连接日志记录器
5. ✅ 建立数据库连接
6. ✅ 连接 IoT 平台 API
7. ✅ 生成测试数据（1,446 行时间序列数据）
8. ✅ 执行自定义函数
9. ✅ 保存测试结果到 CSV 文件
10. ✅ 注册函数到 Maximo Monitor 服务器

---

### 测试输出文件

测试成功后，会在工作目录生成 CSV 文件：

**文件命名格式**：
```
df_TEST_ENTITY_FOR_<FUNCTION_NAME>.csv
```

**示例输出内容**：
```csv
id,evt_timestamp,deviceid,_timestamp,greeting
73001,2026-05-02 02:19:47.774781,73001,2026-05-02 02:19:47.774781,Hello AS_Tester
73002,2026-05-02 02:20:47.774781,73002,2026-05-02 02:20:47.774781,Hello AS_Tester
73003,2026-05-02 02:21:47.774781,73003,2026-05-02 02:21:47.774781,Hello AS_Tester
...
```

**验证命令**：
```bash
# 查看文件大小和修改时间
wsl ls -lh df_TEST_ENTITY_FOR_*.csv

# 查看文件行数
wsl wc -l df_TEST_ENTITY_FOR_*.csv

# 查看文件内容（前10行）
wsl head -10 df_TEST_ENTITY_FOR_HELLOWORLD_MJ.csv

# 查看文件内容（后10行）
wsl tail -10 df_TEST_ENTITY_FOR_HELLOWORLD_MJ.csv
```

---

### 常用操作命令

#### 查看日志和调试

测试脚本使用 DEBUG 级别日志，会显示详细信息：

```bash
# 运行测试并查看详细日志
wsl uv run python local_test_of_function_no_ssl_verify_XX.py 2>&1 | tee test_log.txt
```

**成功标志**：
```
✅ Database connection via SqlAlchemy established.
✅ Native database connection to DB2 established.
✅ http request ... successful. status 200
✅ Generated 1446 rows of time series data
✅ Function registered successfully
```

#### 批量清理测试文件

```bash
# 删除所有测试输出文件
wsl rm -f df_TEST_ENTITY_FOR_*.csv

# 删除日志文件
wsl rm -f test_log.txt
```

#### 查看已注册的函数

```bash
# 查看所有已注册的函数（包括系统函数和自定义函数）
wsl uv run python utils/list_registered_functions.py

# 只查看自定义函数
wsl uv run python utils/list_registered_functions.py --custom-only

# 显示 catalogFunctionId
wsl uv run python utils/list_registered_functions.py --custom-only --show-catalog-id

# 使用 REST API 查看（需要 jq 工具）
wsl bash utils/test_rest_api.sh
```

**命令行参数说明**：
- `--custom-only`: 只列出自定义函数（使用 API 的 customFunctionsOnly 参数）
- `--show-catalog-id`: 显示每个函数的 catalogFunctionId

---

### 最佳实践

1. **命名规范**
   - 函数类名：`FunctionName_YourInitials`（如 `HelloWorld_MJ`）
   - 模块目录：`custom_YourInitials`（如 `custom_MJ`）
   - 测试脚本：`local_test_of_function_no_ssl_YourInitials.py`

2. **开发流程**
   - 先在本地测试验证功能
   - 确认测试输出正确后再注册
   - 使用版本控制管理代码变更

3. **凭证安全**
   - 使用 `credentials_as_dev.json` 存储真实凭证
   - 不要将真实凭证提交到 Git
   - 定期更新凭证密码

4. **测试数据**
   - 保留测试输出文件用于对比
   - 使用有意义的测试数据
   - 验证边界条件和异常情况

5. **函数设计**
   - 保持函数功能单一
   - 添加详细的文档字符串
   - 处理异常情况
   - 记录关键操作日志

---

### 方案 4: 函数管理和 REST API

适用场景：查询、管理已注册的函数，使用 REST API 进行自动化操作

#### 工具脚本概览

项目提供了一套完整的函数管理工具：

| 工具脚本 | 功能 | 使用场景 |
|---------|------|---------|
| `utils/list_registered_functions.py` | 列出所有已注册函数 | 查看函数注册状态 |
| `utils/unregister_function.py` | 注销指定函数 | 删除旧版本函数 |
| `utils/function_utils.py` | 函数管理工具模块 | 提供 Python SDK 方式的函数管理功能 |

#### 步骤 1: 查看已注册的函数

**方法 1: 使用 Python 脚本**

```bash
# 列出所有已注册的函数（包括系统函数和自定义函数）
wsl uv run python utils/list_registered_functions.py
```

**输出示例**：
```
================================================================================
已注册的函数列表 (共 105 个)
================================================================================

系统函数 (103 个):
  1. ActivityDuration (TRANSFORMER)
  2. AggregateTimeInState (AGGREGATOR)
  ...

自定义函数 (2 个):
  104. HelloWorld (TRANSFORMER)
       模块: custom.functions.HelloWorld
  105. HelloWorld_MJ (TRANSFORMER)
       模块: custom_MJ.functions.HelloWorld_MJ
```

**方法 2: 使用 REST API (curl)**

```bash
# 运行完整的 REST API 测试套件
wsl bash utils/test_rest_api.sh
```

**测试内容**：
- ✅ 列出所有函数（105个）
- ✅ 只列出自定义函数（2个）
- ✅ 使用 jq 过滤特定函数
- ℹ️  删除函数示例（不实际执行）
- ℹ️  注册函数示例（不实际执行）

#### 步骤 2: 注销函数

**方法 1: 使用 Python 脚本**

编辑 `utils/unregister_function.py`，设置要注销的函数名：

```python
# 修改函数名
function_name = 'YourFunctionName_XX'
```

运行注销脚本：

```bash
wsl uv run python utils/unregister_function.py
```

**方法 2: 使用 REST API (curl)**

```bash
# 直接使用 curl 删除函数
curl -X DELETE "https://${AS_HOST}/api/catalog/v1/${TENANT_ID}/function/YourFunctionName_XX" \
  -H "X-api-key: ${API_KEY}" \
  -H "X-api-token: ${API_TOKEN}" \
  -k
```

**方法 3: 使用 Python SDK 工具模块（推荐）**

`utils/function_utils.py` 提供了一套完整的函数管理工具，支持安全删除、查询等操作：

```python
from iotfunctions.db import Database
from utils.function_utils import (
    get_registered_functions,
    is_function_registered,
    safe_unregister_function,
    unregister_function
)

# 初始化数据库连接
db = Database(credentials=credentials)

# 1. 获取所有已注册的函数
all_functions = get_registered_functions(db)
print(f"找到 {len(all_functions)} 个函数")

# 2. 只获取自定义函数
custom_functions = get_registered_functions(db, custom_only=True)
print(f"找到 {len(custom_functions)} 个自定义函数")
for func in custom_functions:
    print(f"  - {func['name']} (catalogFunctionId: {func['catalogFunctionId']})")

# 3. 检查函数是否已注册
if is_function_registered(db, 'YourFunctionName_XX'):
    print("函数已注册")
else:
    print("函数未注册")

# 4. 安全地删除函数（先检查再删除，推荐）
success, message = safe_unregister_function(db, 'YourFunctionName_XX')
print(message)

# 5. 直接删除函数（不检查是否存在）
unregister_function(db, 'YourFunctionName_XX')
# 或使用 catalogFunctionId（推荐）
unregister_function(db, '128')
```

**function_utils.py 提供的功能**：

| 函数 | 功能 | 参数 |
|------|------|------|
| `get_registered_functions(db, custom_only=False)` | 获取已注册函数列表 | `custom_only`: 是否只获取自定义函数 |
| `is_function_registered(db, function_name)` | 检查函数是否已注册 | `function_name`: 函数名称 |
| `unregister_function(db, function_name_or_id)` | 注销指定函数 | `function_name_or_id`: 函数名或 catalogFunctionId |
| `safe_unregister_function(db, function_name)` | 安全删除（先检查再删除） | `function_name`: 函数名称 |

**使用示例**：

```python
# 示例 1: 在测试脚本中集成安全删除
from utils.function_utils import safe_unregister_function

# 在注册新函数前，先安全删除旧版本
success, message = safe_unregister_function(db, 'HelloWorld_MJ')
print(message)

# 然后注册新版本
db.register_functions([HelloWorld_MJ])
```

```python
# 示例 2: 批量查询和删除自定义函数
from utils.function_utils import get_registered_functions, unregister_function

# 获取所有自定义函数
custom_functions = get_registered_functions(db, custom_only=True)

# 删除所有自定义函数（使用 catalogFunctionId）
for func in custom_functions:
    catalog_id = func['catalogFunctionId']
    print(f"删除函数: {func['name']} (ID: {catalog_id})")
    unregister_function(db, catalog_id)
```

**优势**：
- ✅ 使用 Python SDK，无需手动构建 HTTP 请求
- ✅ 自动处理 API 凭证和认证
- ✅ 支持 `custom_only` 参数，只获取自定义函数
- ✅ 提供安全删除功能，避免误删
- ✅ 支持使用 catalogFunctionId 进行精确操作

#### 步骤 3: 使用 REST API 管理函数

**查看 API 文档**：

```bash
# 查看完整的 REST API 使用指南
wsl cat utils/REST_API_GUIDE.md
```

**可用的 REST API 端点**：

| 方法 | 端点 | 功能 | 状态 |
|------|------|------|------|
| GET | `/api/catalog/v1/{tenant}/function?customFunctionsOnly=false` | 列出所有函数 | ✅ 可用 |
| GET | `/api/catalog/v1/{tenant}/function?customFunctionsOnly=true` | 列出自定义函数 | ✅ 可用 |
| POST | `/api/catalog/v1/{tenant}/function` | 注册新函数 | ✅ 可用 |
| DELETE | `/api/catalog/v1/{tenant}/function/{catalogFunctionId}` | 删除函数（推荐使用 catalogFunctionId） | ✅ 可用 |
| DELETE | `/api/catalog/v1/{tenant}/function/{name}` | 删除函数（使用函数名） | ✅ 可用 |
| GET | `/api/catalog/v1/{tenant}/function/{catalogFunctionId}` | 获取单个函数 | ❌ 不可用 (405) |

**重要说明**：
- 函数列表返回的每个函数都包含 `catalogFunctionId` 字段，这是函数的唯一标识符
- **推荐使用 `catalogFunctionId` 而不是函数名进行删除和注册操作**，以确保操作的精确性
- GET 单个函数的端点不可用，建议使用列表查询后过滤的方式获取函数详情

**Python SDK 示例**：

```python
from iotfunctions.db import Database

# 初始化数据库连接
db = Database(credentials=credentials)

# 列出所有函数
response = db.http_request(
    object_type='allFunctions',
    object_name='allFunctions',
    request='GET',
    payload={}
)
functions = response.json()
print(f"找到 {len(functions)} 个函数")

# 列出自定义函数
response = db.http_request(
    object_type='allFunctions',
    object_name='allFunctions',
    request='GET',
    payload={'customFunctionsOnly': True}
)
custom_functions = response.json()
print(f"找到 {len(custom_functions)} 个自定义函数")

# 显示函数的 catalogFunctionId
for func in custom_functions:
    print(f"  - {func['name']} (catalogFunctionId: {func['catalogFunctionId']})")

# 删除函数（推荐使用 catalogFunctionId）
catalog_function_id = custom_functions[0]['catalogFunctionId']
response = db.http_request(
    object_type='function',
    object_name=str(catalog_function_id),  # 使用 catalogFunctionId
    request='DELETE'
)

# 或者使用函数名删除（不推荐，可能存在重名）
response = db.http_request(
    object_type='function',
    object_name='YourFunctionName',  # 使用函数名
    request='DELETE'
)
```

**curl 命令示例**：

```bash
# 设置环境变量
export TENANT_ID="ws1"
export AS_HOST="ws1.api.monitor.inst1.apps.itz-7l9v61.infra01-lb.dal14.techzone.ibm.com"
export API_KEY="your-api-key"
export API_TOKEN="your-api-token"

# 列出所有函数
curl -X GET "https://${AS_HOST}/api/catalog/v1/${TENANT_ID}/function?customFunctionsOnly=false" \
  -H "X-api-key: ${API_KEY}" \
  -H "X-api-token: ${API_TOKEN}" \
  -k | jq '.'

# 列出自定义函数
curl -X GET "https://${AS_HOST}/api/catalog/v1/${TENANT_ID}/function?customFunctionsOnly=true" \
  -H "X-api-key: ${API_KEY}" \
  -H "X-api-token: ${API_TOKEN}" \
  -k | jq '.'

# 查找特定函数并获取其 catalogFunctionId
curl -X GET "https://${AS_HOST}/api/catalog/v1/${TENANT_ID}/function?customFunctionsOnly=false" \
  -H "X-api-key: ${API_KEY}" \
  -H "X-api-token: ${API_TOKEN}" \
  -k | jq '.[] | select(.name=="HelloWorld_MJ") | {name, catalogFunctionId}'

# 删除函数（推荐使用 catalogFunctionId）
# 首先获取 catalogFunctionId
CATALOG_ID=$(curl -s -X GET "https://${AS_HOST}/api/catalog/v1/${TENANT_ID}/function?customFunctionsOnly=true" \
  -H "X-api-key: ${API_KEY}" \
  -H "X-api-token: ${API_TOKEN}" \
  -k | jq -r '.[] | select(.name=="YourFunctionName") | .catalogFunctionId')

# 使用 catalogFunctionId 删除
curl -X DELETE "https://${AS_HOST}/api/catalog/v1/${TENANT_ID}/function/${CATALOG_ID}" \
  -H "X-api-key: ${API_KEY}" \
  -H "X-api-token: ${API_TOKEN}" \
  -k

# 或者直接使用函数名删除（不推荐）
curl -X DELETE "https://${AS_HOST}/api/catalog/v1/${TENANT_ID}/function/YourFunctionName" \
  -H "X-api-key: ${API_KEY}" \
  -H "X-api-token: ${API_TOKEN}" \
  -k
```

#### 步骤 4: 自动化工作流

**示例：完整的函数更新流程**

```bash
#!/bin/bash
# 自动化函数更新脚本

FUNCTION_NAME="YourFunctionName_XX"

echo "🔍 检查函数是否已注册..."
wsl uv run python utils/list_registered_functions.py | grep "$FUNCTION_NAME"

if [ $? -eq 0 ]; then
    echo "🗑️  删除旧版本函数..."
    # 使用 REST API 删除
    curl -X DELETE "https://${AS_HOST}/api/catalog/v1/${TENANT_ID}/function/${FUNCTION_NAME}" \
      -H "X-api-key: ${API_KEY}" \
      -H "X-api-token: ${API_TOKEN}" \
      -k
fi

echo "🧪 运行测试并注册新版本..."
wsl uv run python local_test_of_function_no_ssl_verify_XX.py

echo "✅ 验证函数注册..."
wsl uv run python utils/list_registered_functions.py | grep "$FUNCTION_NAME"
```

#### 步骤 5: 函数管理最佳实践

1. **查询前先列表**
   - 使用 `list_registered_functions.py` 查看所有函数
   - 确认函数名称和状态后再操作

2. **安全删除**
   - 使用 `safe_unregister_function()` 而不是直接删除
   - 先检查函数是否存在，避免不必要的错误

3. **REST API 使用**
   - 优先使用 Python SDK (`db.http_request()`)
   - curl 适合快速测试和脚本自动化
   - **推荐使用 catalogFunctionId 而不是函数名进行删除操作**
   - 注意 GET 单个函数端点不可用，使用列表过滤
   - 函数列表返回的每个函数都包含 `catalogFunctionId` 字段

4. **批量操作**
   - 使用 bash 脚本批量管理多个函数
   - 结合 jq 工具处理 JSON 响应
   - 记录操作日志便于追踪

5. **错误处理**
   - 检查 HTTP 状态码（200 成功，204 无内容，405 方法不允许）
   - 处理函数不存在的情况
   - 验证 API 凭证有效性
   - 使用 catalogFunctionId 可以避免函数名冲突问题

#### 关于 catalogFunctionId

每个注册的函数都有一个唯一的 `catalogFunctionId`，这是函数在系统中的唯一标识符。

**获取 catalogFunctionId**：

```python
# Python 方式
from iotfunctions.db import Database

db = Database(credentials=credentials)
response = db.http_request(
    object_type='allFunctions',
    object_name='allFunctions',
    request='GET',
    payload={'customFunctionsOnly': True}
)
functions = response.json()

for func in functions:
    print(f"{func['name']}: catalogFunctionId = {func['catalogFunctionId']}")
```

```bash
# curl 方式
curl -X GET "https://${AS_HOST}/api/catalog/v1/${TENANT_ID}/function?customFunctionsOnly=true" \
  -H "X-api-key: ${API_KEY}" \
  -H "X-api-token: ${API_TOKEN}" \
  -k | jq '.[] | {name, catalogFunctionId}'
```

**使用 catalogFunctionId 的优势**：
- ✅ 唯一标识，避免函数名冲突
- ✅ 精确操作，不会误删同名函数
- ✅ 系统推荐的最佳实践
- ✅ 适用于自动化脚本和批量操作


## 常见问题

### Windows 环境问题

**问题**: 在 Windows 上遇到 `SQL1042C` 数据库连接错误

**解决方案**: 使用 WSL 环境
- Windows 上的 DB2 CLI 驱动程序存在兼容性问题
- WSL 环境中一切正常工作
- 所有命令都使用 `wsl` 前缀

### DB2 连接错误 (SQL30081N)

**问题**: `SQL30081N A communication error has been detected`

**解决方案**: 使用自动证书更新功能
- 项目已集成 DB2 SSL 证书自动更新功能
- 每次运行测试脚本时自动下载最新证书
- 使用 `quick_setup(credentials)` 一键设置
- 如果下载失败，自动回退使用现有证书

**手动下载证书**（如需要）：
```python
from utils.db2_utils import download_db2_certificate

# 手动下载证书
success = download_db2_certificate(
    db2_host="your-db2-host.com",
    db2_port=443,
    cert_file="db2_certificate.pem"
)
```

### SSL 证书验证错误

**问题**: `SSL: CERTIFICATE_VERIFY_FAILED`

**解决方案**: 使用 `local_test_of_function_no_ssl_verify.py`
- 该脚本已禁用 SSL 验证（仅用于开发/测试）
- 使用 `quick_setup(credentials)` 自动配置
- 包含必要的 monkey patch

### Python 3.11 兼容性

**问题**: `cannot import name 'getargspec' from 'inspect'`

**解决方案**: 使用 `local_test_of_function_no_ssl.py`
- 该脚本包含 Python 3.11 兼容性修复
- 自动将 `getargspec` 映射到 `getfullargspec`

### SQLAlchemy 版本问题

**问题**: `'str' object has no attribute '_execute_on_connection'`

**解决方案**: 降级到 SQLAlchemy 1.4.53
```bash
wsl uv pip install sqlalchemy==1.4.53
```

### 函数重复注册

**问题**: `Duplicate catalog function name`

**解决方案**: 先注销再注册
```bash
wsl uv run python unregister_function.py
wsl uv run python local_test_of_function_no_ssl.py
```

### 缺少模块错误

如果遇到 `ModuleNotFoundError`,请确保已安装所有依赖包:

```bash
wsl uv pip install <missing_package>
```

## 技术细节

### 已安装的包版本

- iotfunctions==8.3.1 (IBM Watson IoT Functions SDK)
- ibm-db==3.2.9
- ibm-db-sa==0.4.4
- sqlalchemy==1.4.53 (降级以兼容)
- psycopg2-binary==2.9.12
- pyarrow==24.0.0
- numpy==2.4.4
- pandas==3.0.2
- scikit-learn==1.8.0
- scipy==1.17.1
- tabulate==0.10.0
- statsmodels==0.14.6
- ibm-cos-sdk==2.16.2

### 关键修复

1. **SSL 验证禁用**: urllib3 PoolManager monkey patch
2. **Python 3.11 兼容**: inspect.getargspec 映射
3. **SQLAlchemy 降级**: 1.4.53 版本兼容 iotfunctions
4. **WSL 环境**: 解决 Windows DB2 驱动问题

## 参考资料

- [IBM Maximo Monitor 文档](https://www.ibm.com/docs/en/maximo-monitor)
- [IBM Watson IoT Functions GitHub](https://github.com/ibm-watson-iot/functions)
- [uv 文档](https://github.com/astral-sh/uv)

## 许可证

请参考项目许可证文件。
