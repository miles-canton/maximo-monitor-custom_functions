# maximo-monitor-custom_functions

Maximo Monitor 自定义函数开发和测试项目

## 项目结构

```
.
├── custom/                      # 自定义函数模块
│   ├── __init__.py
│   └── functions.py            # 自定义函数实现
├── custom_MJ/                   # 自定义函数模块 (MJ)
│   ├── __init__.py
│   └── functions.py            # 自定义函数实现
├── credentials_as_dev.json      # 数据库和 IoT 平台凭证
├── local_test_of_function.py    # 本地测试脚本
└── README.md                    # 本文档
```

## 环境设置

### 前置要求

- Python 3.11
- uv (Python 包管理工具)
- Git

### 1. 创建虚拟环境

使用 uv 创建 Python 3.11 虚拟环境:

```bash
uv venv --python 3.11
```

这将创建一个 `.venv` 目录,包含 Python 3.11 虚拟环境。

### 2. 安装 IBM Watson IoT Functions SDK

#### 2.1 安装 ibm-db

首先安装最新版本的 ibm-db 以避免兼容性问题:

```bash
uv pip install ibm-db --upgrade
```

#### 2.2 安装 iotfunctions (不含依赖)

```bash
uv pip install git+https://github.com/ibm-watson-iot/functions@production --no-deps
```

#### 2.3 安装其他依赖包

```bash
uv pip install dill==0.3.0 numpy pandas scikit-learn scipy lxml sqlalchemy requests urllib3 ibm-cos-sdk
```

#### 2.4 安装数据库相关包

```bash
uv pip install psycopg2-binary pyarrow ibm-db-sa tabulate statsmodels
```

### 3. 配置凭证

编辑 `credentials_as_dev.json` 文件,填入您的数据库和 IoT 平台凭证:

```json
{
    "tenantId": "your_tenant_id",
    "db2": {
        "username": "your_username",
        "password": "your_password",
        "databaseName": "BLUDB",
        "port": 50000,
        "httpsUrl": "jdbc:db2://your_host:50000/BLUDB",
        "host": "your_host",
        "security": "SSL"
    },
    "iotp": {
        "url": "https://your_iot_url",
        "orgId": "your_org_id",
        "host": "your_iot_host",
        "port": 443,
        "asHost": "your_as_host",
        "apiKey": "your_api_key",
        "apiToken": "your_api_token"
    }
}
```

**注意**: 不要将包含真实凭证的文件提交到版本控制系统。

## 运行测试

### 本地测试自定义函数

```bash
uv run python local_test_of_function.py
```

测试脚本将:
1. 加载凭证
2. 连接到数据库
3. 执行自定义函数的本地测试
4. 将测试结果写入文件
5. 注册函数到服务器

### 测试输出

测试结果将保存在工作目录中,文件名格式为:
```
df_test_entity_for_<function_name>
```

## 开发自定义函数

### 1. 创建函数

在 `custom/functions.py` 或 `custom_MJ/functions.py` 中定义您的自定义函数:

```python
from iotfunctions.base import BaseTransformer

class HelloWorld_MJ(BaseTransformer):
    def __init__(self, name, greeting_col):
        super().__init__()
        self.name = name
        self.greeting_col = greeting_col
    
    def execute(self, df):
        df[self.greeting_col] = f"Hello {self.name}!"
        return df
```

### 2. 本地测试

在 `local_test_of_function.py` 中导入并测试您的函数:

```python
from custom.functions import HelloWorld_MJ

fn = HelloWorld_MJ(name='AS_Tester', greeting_col='greeting')
fn.execute_local_test(db=db, db_schema=db_schema)
```

### 3. 注册函数

```python
db.register_functions([HelloWorld_MJ])
```

## 已安装的包

- iotfunctions==8.3.1 (IBM Watson IoT Functions SDK)
- ibm-db==3.2.9
- ibm-db-sa==0.4.4
- psycopg2-binary==2.9.12
- pyarrow==24.0.0
- numpy==2.4.4
- pandas==3.0.2
- scikit-learn==1.8.0
- scipy==1.17.1
- sqlalchemy==2.0.49
- tabulate==0.10.0
- statsmodels==0.14.6
- ibm-cos-sdk==2.16.2
- 以及其他相关依赖包

## 常见问题

### 数据库连接错误 (SQL1042C)

如果遇到 `SQL1042C` 错误,请检查:

1. 数据库服务器是否在线和可访问
2. 网络连接和防火墙设置
3. `credentials_as_dev.json` 中的凭证是否正确
4. 如果使用 SSL,确保 `db2_certificate.pem` 文件存在

### 缺少模块错误

如果遇到 `ModuleNotFoundError`,请确保已安装所有依赖包:

```bash
uv pip install <missing_package>
```

## Git 操作

### 提交更改

```bash
# 查看状态
git status

# 添加文件
git add .

# 提交
git commit -m "描述您的更改"

# 推送到远程
git push origin main
```

## 参考资料

- [IBM Maximo Monitor 文档](https://www.ibm.com/docs/en/maximo-monitor)
- [IBM Watson IoT Functions GitHub](https://github.com/ibm-watson-iot/functions)
- [uv 文档](https://github.com/astral-sh/uv)

## 许可证

请参考项目许可证文件。
