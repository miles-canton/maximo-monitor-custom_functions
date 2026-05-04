"""
DB2 工具模块
提供 DB2 连接调试和 SSL 证书管理功能
"""

import ssl
import urllib3
import subprocess
import os
from pathlib import Path


def download_db2_certificate(host: str, port: int = 443, output_file: str = "db2_certificate.pem") -> str:
    """
    从 DB2 服务器下载 SSL 证书
    
    Args:
        host: DB2 服务器主机名
        port: DB2 服务器端口（默认 443）
        output_file: 输出证书文件名（默认 "db2_certificate.pem"）
    
    Returns:
        str: 证书文件的绝对路径
    
    Raises:
        RuntimeError: 如果证书下载失败
    """
    try:
        # 使用 openssl 命令下载证书
        cmd = f"echo | openssl s_client -connect {host}:{port} -showcerts 2>/dev/null | sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p'"
        
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        
        if not result.stdout or "BEGIN CERTIFICATE" not in result.stdout:
            raise RuntimeError(f"Failed to download certificate from {host}:{port}")
        
        # 写入证书文件
        cert_path = Path(output_file).resolve()
        with open(cert_path, 'w') as f:
            f.write(result.stdout)
        
        print(f"✅ 证书已下载到: {cert_path}")
        print(f"   证书大小: {cert_path.stat().st_size} 字节")
        
        return str(cert_path)
        
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to execute openssl command: {e}")
    except Exception as e:
        raise RuntimeError(f"Failed to download certificate: {e}")


def setup_ssl_no_verify():
    """
    配置 urllib3 禁用 SSL 证书验证
    这会全局影响所有使用 urllib3 的 HTTPS 请求
    
    警告: 仅用于开发和测试环境
    """
    # 禁用 SSL 警告
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # Monkey patch urllib3 to disable SSL verification globally
    original_poolmanager_init = urllib3.PoolManager.__init__
    
    def patched_poolmanager_init(self, *args, **kwargs):
        kwargs['cert_reqs'] = ssl.CERT_NONE
        kwargs['assert_hostname'] = False
        return original_poolmanager_init(self, *args, **kwargs)
    
    urllib3.PoolManager.__init__ = patched_poolmanager_init
    
    print("✅ SSL 证书验证已禁用（仅用于开发/测试）")


def setup_db2_connection_logger(verbose=False):
    """
    设置 DB2 连接字符串日志记录器
    拦截 ibm_db.connect() 调用并打印实际的连接字符串
    密码会自动脱敏
    
    Args:
        verbose: 是否打印每次连接（默认 False，只打印第一次）
    
    Returns:
        function: 原始的 ibm_db.connect 函数（用于恢复）
    """
    try:
        import ibm_db
    except ImportError:
        raise ImportError("ibm_db module not found. Please install it first.")
    
    original_ibm_db_connect = ibm_db.connect
    
    # 用于跟踪是否已打印过连接字符串
    connection_printed = {'count': 0}
    
    def patched_ibm_db_connect(dsn, user='', password='', options=None):
        """
        拦截 ibm_db.connect 调用以打印实际的连接字符串
        这有助于调试 DB2 连接问题
        """
        # 只在第一次或 verbose 模式下打印
        if verbose or connection_printed['count'] == 0:
            print("\n" + "="*80)
            print("DB2 连接字符串 (Connection String):")
            print("="*80)
            
            # 脱敏密码 - 处理 PWD=xxx 格式
            import re
            masked_dsn = dsn
            
            # 方法1: 替换 PWD=xxx; 格式
            masked_dsn = re.sub(r'PWD=[^;]+', 'PWD=***', masked_dsn)
            
            # 方法2: 如果密码作为参数传递，也替换它
            if password:
                masked_dsn = masked_dsn.replace(password, '***')
            
            print(masked_dsn)
            print("="*80 + "\n")
            
            connection_printed['count'] += 1
        
        if options is None:
            return original_ibm_db_connect(dsn, user, password)
        else:
            return original_ibm_db_connect(dsn, user, password, options)
    
    ibm_db.connect = patched_ibm_db_connect
    
    print("✅ DB2 连接字符串日志记录器已启用（仅显示首次连接）")
    
    return original_ibm_db_connect


def restore_db2_connection(original_connect):
    """
    恢复原始的 ibm_db.connect 函数
    
    Args:
        original_connect: 原始的 ibm_db.connect 函数
    """
    try:
        import ibm_db
        ibm_db.connect = original_connect
        print("✅ DB2 连接已恢复为原始函数")
    except ImportError:
        pass


def setup_all(db2_host: str = None, db2_port: int = 443, cert_file: str = "db2_certificate.pem"):
    """
    一键设置所有 DB2 调试功能
    
    Args:
        db2_host: DB2 服务器主机名（如果提供，会下载证书）
        db2_port: DB2 服务器端口（默认 443）
        cert_file: 证书文件名（默认 "db2_certificate.pem"）
    
    Returns:
        dict: 包含设置信息的字典
    """
    result = {
        "ssl_no_verify": False,
        "db2_logger": False,
        "certificate": None
    }
    
    print("\n" + "="*80)
    print("DB2 调试工具初始化")
    print("="*80 + "\n")
    
    # 1. 设置 SSL 禁用验证
    try:
        setup_ssl_no_verify()
        result["ssl_no_verify"] = True
    except Exception as e:
        print(f"⚠️  SSL 设置失败: {e}")
    
    # 2. 下载证书（如果提供了主机名）
    if db2_host:
        try:
            cert_path = download_db2_certificate(db2_host, db2_port, cert_file)
            result["certificate"] = cert_path
        except Exception as e:
            print(f"⚠️  证书下载失败: {e}")
    
    # 3. 设置 DB2 连接日志记录器
    try:
        original_connect = setup_db2_connection_logger()
        result["db2_logger"] = True
        result["original_connect"] = original_connect
    except Exception as e:
        print(f"⚠️  DB2 日志记录器设置失败: {e}")
    
    print("\n" + "="*80)
    print("初始化完成")
    print("="*80 + "\n")
    
    return result


# 便捷函数
def quick_setup(credentials: dict):
    """
    根据 credentials 字典快速设置
    
    Args:
        credentials: 包含 DB2 配置的字典
    
    Returns:
        dict: 设置结果
    """
    db2_config = credentials.get('db2', {})
    host = db2_config.get('host')
    port = db2_config.get('port', 443)
    cert_file = db2_config.get('certificate', 'db2_certificate.pem')
    
    return setup_all(db2_host=host, db2_port=port, cert_file=cert_file)


if __name__ == "__main__":
    # 示例用法
    print("DB2 工具模块")
    print("\n使用示例:")
    print("1. 下载证书:")
    print("   from db2_utils import download_db2_certificate")
    print("   download_db2_certificate('your-db2-host.com', 443)")
    print("\n2. 设置 SSL 禁用验证:")
    print("   from db2_utils import setup_ssl_no_verify")
    print("   setup_ssl_no_verify()")
    print("\n3. 设置 DB2 连接日志:")
    print("   from db2_utils import setup_db2_connection_logger")
    print("   setup_db2_connection_logger()")
    print("\n4. 一键设置所有功能:")
    print("   from db2_utils import setup_all")
    print("   setup_all(db2_host='your-db2-host.com')")
    print("\n5. 根据 credentials 快速设置:")
    print("   from db2_utils import quick_setup")
    print("   quick_setup(credentials)")

# Made with Bob
