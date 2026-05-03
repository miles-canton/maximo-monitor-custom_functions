# maximo-monitor-custom_functions

Maximo Monitor 自定义函数开发和测试项目

## 项目结构

```
.
├── custom/                           # 自定义函数模块 (示例)
│   ├── __init__.py
│   └── functions.py                 # 自定义函数实现
├── custom_MJ/                        # 自定义函数模块 (MJ 示例)
│   ├── __init__.py
│   └── functions.py                 # 自定义函数实现
├── credentials_as.json               # 凭证模板 (测试脚本使用)
├── credentials_as_dev.json           # 真实凭证备份 (gitignore)
├── local_test_of_function_no_ssl.py  # 推荐测试脚本 (含修复)
├── unregister_function.py            # 函数注销工具
├── requirements.txt                  # Python 依赖包列表
├── .gitignore                        # Git 忽略文件配置
└── README.md                         # 本文档
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

- **`credentials_as.json`** - 您的实际凭证文件 (测试脚本使用此文件)
- **`credentials_as_dev.json`** - 开发者的凭证备份 (已在 .gitignore 中排除)

#### 凭证文件说明

仓库中的 `credentials_as.json` 是一个**模板文件**,包含占位符而非真实凭证。

#### 首次设置

编辑 `credentials_as.json`,填入您的真实数据库和 IoT 平台凭证:

```json
{
    "tenantId": "your_tenant_id",
    "db2": {
        "username": "your_db2_username",
        "password": "your_db2_password",
        "databaseName": "BLUDB",
        "port": 50000,
        "httpsUrl": "jdbc:db2://your_db2_host:50000/BLUDB",
        "host": "your_db2_host"
    },
    "iotp": {
        "url": "https://your_iot_url/api/v0002",
        "orgId": "your_org_id",
        "host": "your_iot_host",
        "port": 443,
        "asHost": "your_as_host",
        "apiKey": "your_api_key",
        "apiToken": "your_api_token"
    },
    "_verify_ssl": false
}
```

#### 备份您的凭证 (可选)

如果您想保留一份不会被 Git 跟踪的凭证备份:

```bash
# 复制到 credentials_as_dev.json (此文件已在 .gitignore 中)
wsl cp credentials_as.json credentials_as_dev.json
```

**重要提示**:
- ⚠️ `credentials_as.json` - 测试脚本使用的文件,填入真实凭证后**不要提交到 Git**
- ✅ `credentials_as_dev.json` - 已在 .gitignore 中排除,可以安全地存储真实凭证
- 📝 提交代码前,请确保 `credentials_as.json` 中只包含占位符,不包含真实密钥

## 测试和开发工作流程

### 测试脚本说明

项目包含两个主要测试脚本:

1. **`local_test_of_function_no_ssl.py`** - 推荐使用
   - 包含 SSL 验证禁用(用于开发/测试环境)
   - 包含 Python 3.11 兼容性修复
   - 在 WSL 环境中完美运行

2. **`unregister_function.py`** - 函数管理工具
   - 用于注销已注册的函数
   - 允许重新注册同名函数

### 完整测试流程

#### 方法 1: 首次测试和注册

```bash
# 运行测试并注册函数
wsl uv run python local_test_of_function_no_ssl.py
```

测试脚本将:
1. 加载凭证
2. 连接到数据库
3. 连接到 IoT 平台 API
4. 生成测试数据 (1,446 行)
5. 执行自定义函数
6. 将测试结果写入 CSV 文件
7. 注册函数到服务器

#### 方法 2: 重新测试和注册(生成新测试文件)

如果函数已存在,需要先注销再重新注册:

```bash
# 步骤 1: 删除旧测试文件
wsl rm -f df_TEST_ENTITY_FOR_HELLOWORLD_MJ.csv

# 步骤 2: 注销现有函数
wsl uv run python unregister_function.py

# 步骤 3: 重新测试和注册(自动生成新测试文件)
wsl uv run python local_test_of_function_no_ssl.py
```

#### 方法 3: 仅注销函数

```bash
wsl uv run python unregister_function.py
```

**修改要注销的函数名**: 编辑 `unregister_function.py` 中的 `function_name` 变量

### 测试输出

测试结果将保存在工作目录中,文件名格式为:
```
df_TEST_ENTITY_FOR_<FUNCTION_NAME>.csv
```

**示例输出**:
```csv
id,evt_timestamp,deviceid,_timestamp,greeting
73001,2026-05-02 02:19:47.774781,73001,2026-05-02 02:19:47.774781,Hello AS_Tester
73002,2026-05-02 02:20:47.774781,73002,2026-05-02 02:20:47.774781,Hello AS_Tester
...
```

### 验证测试结果

```bash
# 查看文件信息
wsl ls -lh df_TEST_ENTITY_FOR_*.csv

# 查看文件内容(前10行)
wsl head -10 df_TEST_ENTITY_FOR_HELLOWORLD_MJ.csv
```

## 开发自定义函数

### 快速开始: 测试您自己的函数

如果您想测试自己的自定义函数,请按照以下步骤操作:

#### 步骤 1: 复制并重命名函数模块

```bash
# 复制 custom 文件夹
wsl cp -r custom custom_XX

# XX 替换为您的名字,例如: custom_John, custom_Alice
```

#### 步骤 2: 修改函数类名

编辑 `custom_XX/functions.py`,将类名改为包含您名字的格式:

```python
from iotfunctions.base import BaseTransformer

# 将 HelloWorld_MJ 改为 HelloWorld_XX (XX 是您的名字)
class HelloWorld_XX(BaseTransformer):
    def __init__(self, name, greeting_col):
        super().__init__()
        self.name = name
        self.greeting_col = greeting_col
    
    def execute(self, df):
        df[self.greeting_col] = f"Hello {self.name}!"
        return df
```

**示例**:
- `HelloWorld_John`
- `HelloWorld_Alice`
- `HelloWorld_Bob`

#### 步骤 3: 修改测试脚本

编辑 `local_test_of_function_no_ssl.py`,修改两处:

**3.1 修改 import 语句**:
```python
# 原来:
from custom_MJ.functions import HelloWorld_MJ

# 改为:
from custom_XX.functions import HelloWorld_XX
```

**3.2 修改类名引用**:
```python
# 原来:
fn = HelloWorld_MJ(
    name='AS_Tester',
    greeting_col='greeting'
)

# 改为:
fn = HelloWorld_XX(
    name='AS_Tester',
    greeting_col='greeting'
)
```

以及:
```python
# 原来:
db.register_functions([HelloWorld_MJ])

# 改为:
db.register_functions([HelloWorld_XX])
```

#### 步骤 4: 运行测试

```bash
# 运行测试并注册您的函数
wsl uv run python local_test_of_function_no_ssl.py
```

测试成功后,您将看到:
- 生成的测试数据文件: `df_TEST_ENTITY_FOR_HELLOWORLD_XX.csv`
- 函数成功注册到服务器 (HTTP 200)

#### 步骤 5: 如需重新测试

```bash
# 删除旧测试文件
wsl rm -f df_TEST_ENTITY_FOR_HELLOWORLD_XX.csv

# 注销函数 (需要先修改 unregister_function.py 中的函数名)
wsl uv run python unregister_function.py

# 重新测试
wsl uv run python local_test_of_function_no_ssl.py
```

### 详细说明: 创建自定义函数

#### 1. 函数结构

在 `custom_XX/functions.py` 中定义您的自定义函数:

```python
from iotfunctions.base import BaseTransformer

class YourFunctionName(BaseTransformer):
    def __init__(self, param1, param2, output_col):
        super().__init__()
        self.param1 = param1
        self.param2 = param2
        self.output_col = output_col
    
    def execute(self, df):
        # 您的业务逻辑
        df[self.output_col] = df['input_col'] * self.param1 + self.param2
        return df
```

#### 2. 本地测试

在 `local_test_of_function_no_ssl.py` 中导入并测试您的函数:

```python
from custom_XX.functions import YourFunctionName

fn = YourFunctionName(
    param1=10,
    param2=5,
    output_col='result'
)
fn.execute_local_test(db=db, db_schema=db_schema)
```

#### 3. 注册函数

```python
db.register_functions([YourFunctionName])
```

## 开发工作流程

### 开发新函数

1. 在 `custom/functions.py` 或 `custom_MJ/functions.py` 中编写函数
2. 运行测试脚本验证功能
3. 查看生成的 CSV 文件确认结果
4. 函数自动注册到服务器

### 更新现有函数

1. 修改 `custom/functions.py` 中的函数代码
2. 删除旧测试文件
3. 注销旧版本函数
4. 重新运行测试并注册

### 调试技巧

**查看详细日志**:
测试脚本使用 DEBUG 级别日志,会显示:
- 数据库连接状态
- API 请求和响应
- 数据生成过程
- 函数执行细节

**常见成功标志**:
```
✅ Database connection via SqlAlchemy established.
✅ Native database connection to DB2 established.
✅ http request ... successful. status 200
✅ Generated 1446 rows of time series data
```

## 常见问题

### Windows 环境问题

**问题**: 在 Windows 上遇到 `SQL1042C` 数据库连接错误

**解决方案**: 使用 WSL 环境
- Windows 上的 DB2 CLI 驱动程序存在兼容性问题
- WSL 环境中一切正常工作
- 所有命令都使用 `wsl` 前缀

### SSL 证书验证错误

**问题**: `SSL: CERTIFICATE_VERIFY_FAILED`

**解决方案**: 使用 `local_test_of_function_no_ssl.py`
- 该脚本已禁用 SSL 验证(仅用于开发/测试)
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
