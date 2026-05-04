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
├── credentials_as.json                          # 凭证模板 (测试脚本使用)
├── credentials_as_dev.json                      # 真实凭证备份 (gitignore)
├── db2_certificate.pem                          # DB2 SSL 证书文件
├── db2_utils.py                                 # DB2 数据库工具函数
├── local_test_of_function_no_ssl_verify.py      # 通用测试脚本 (含修复)
├── local_test_of_function_no_ssl_verify_MJ.py   # MJ 示例测试脚本
├── unregister_function.py                       # 函数注销工具
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
- `db2.certificate`: SSL 证书文件路径
- `iotp.apiKey`: IoT 平台 API 密钥 (需要替换 YOUR_API_KEY)
- `iotp.apiToken`: IoT 平台 API 令牌 (需要替换 YOUR_API_TOKEN)
- `_verify_ssl`: 是否验证 SSL 证书 (false 用于开发/测试环境)

**重要提示**:
- ⚠️ `credentials_as.json` - 凭证模板文件,**不要直接修改此文件填写真实凭证**
- ✅ `credentials_as_dev.json` - 已在 .gitignore 中排除,可以安全地存储真实凭证
- 📝 测试脚本默认读取 `credentials_as_dev.json`,如果不存在则读取 `credentials_as.json`
- 🔒 提交代码前,请确保 `credentials_as.json` 中只包含占位符,不包含真实密钥

## 使用方案

### 方案概述

本项目提供三种主要使用方案：

1. **快速测试现有函数** - 直接运行示例函数进行测试
2. **开发新的自定义函数** - 创建并测试您自己的函数
3. **更新和重新部署函数** - 修改现有函数并重新注册

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

#### 步骤 3: 验证结果

```bash
# 查看生成的测试文件
wsl ls -lh df_TEST_ENTITY_FOR_*.csv

# 查看测试数据（前10行）
wsl head -10 df_TEST_ENTITY_FOR_HELLOWORLD_MJ.csv
```

**预期输出**：
- ✅ 数据库连接成功
- ✅ 生成 1,446 行测试数据
- ✅ 函数执行成功
- ✅ 函数注册成功 (HTTP 200)
- ✅ 生成 CSV 测试文件

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

编辑 `unregister_function.py`，设置要注销的函数名：

```python
# 修改函数名为您要注销的函数
function_name = 'YourFunctionName_XX'
```

运行注销脚本：

```bash
wsl uv run python unregister_function.py
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
| `local_test_of_function_no_ssl_verify_MJ.py` | 示例测试脚本 | 测试 HelloWorld_MJ 函数 |
| `local_test_of_function_no_ssl_verify.py` | 通用测试脚本 | 可复制并修改用于测试自定义函数 |
| `unregister_function.py` | 函数注销工具 | 用于注销已注册的函数 |

**测试脚本功能**：
1. ✅ 加载凭证配置
2. ✅ 建立数据库连接
3. ✅ 连接 IoT 平台 API
4. ✅ 生成测试数据（1,446 行时间序列数据）
5. ✅ 执行自定义函数
6. ✅ 保存测试结果到 CSV 文件
7. ✅ 注册函数到 Maximo Monitor 服务器

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
# 查看函数注册状态（需要修改脚本添加查询功能）
# 或通过 Maximo Monitor UI 查看
```

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
