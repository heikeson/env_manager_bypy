import ctypes
import sys

class SecurityManager:
    """
    安全管理类，用于权限验证和安全检查
    """

    def __init__(self):
        """
        初始化安全管理器
        """
        # 系统关键环境变量列表
        self.CRITICAL_ENV_VARS = [
            "PATH",
            "SYSTEMROOT",
            "WINDIR",
            "PROGRAMFILES",
            "PROGRAMFILES(X86)",
            "PROGRAMDATA",
            "APPDATA",
            "LOCALAPPDATA",
            "TEMP",
            "TMP"
        ]

    def is_admin(self):
        """
        检查当前是否以管理员权限运行
        
        Returns:
            bool: 是否具有管理员权限
        """
        try:
            # 检查是否具有管理员权限
            return ctypes.windll.shell32.IsUserAnAdmin()
        except Exception as e:
            print(f"Error checking admin status: {e}")
            return False

    def request_admin(self):
        """
        请求管理员权限
        
        Returns:
            bool: 是否成功获取管理员权限
        """
        try:
            # 获取当前脚本路径
            script = sys.argv[0]
            # 使用ShellExecute以管理员权限重新启动脚本
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, script, None, 1
            )
            # 退出当前进程
            sys.exit(0)
        except Exception as e:
            print(f"Error requesting admin: {e}")
            return False

    def check_environment_variable_safety(self, name):
        """
        检查环境变量是否安全（非系统关键变量）
        
        Args:
            name (str): 环境变量名
            
        Returns:
            bool: 是否安全
        """
        # 检查是否为系统关键环境变量
        return name.upper() not in self.CRITICAL_ENV_VARS

    def get_critical_env_vars(self):
        """
        获取系统关键环境变量列表
        
        Returns:
            list: 系统关键环境变量列表
        """
        return self.CRITICAL_ENV_VARS

if __name__ == "__main__":
    # 测试代码
    security = SecurityManager()
    
    # 检查是否为管理员
    print(f"Is admin: {security.is_admin()}")
    
    # 检查环境变量安全性
    test_vars = ["PATH", "TEMP", "MY_CUSTOM_VAR"]
    for var in test_vars:
        print(f"{var} is safe: {security.check_environment_variable_safety(var)}")
    
    # 查看系统关键环境变量列表
    print("\nCritical environment variables:")
    for var in security.get_critical_env_vars():
        print(f"- {var}")
