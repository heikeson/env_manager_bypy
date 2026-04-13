import winreg
import os

class EnvironmentVariableManager:
    """
    环境变量管理类，用于管理Windows系统的环境变量
    """

    def __init__(self):
        """
        初始化环境变量管理器
        """
        # 系统环境变量注册表路径
        self.SYSTEM_ENV_REG_PATH = r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
        # 用户环境变量注册表路径
        self.USER_ENV_REG_PATH = r"Environment"

    def get_environment_variables(self, scope):
        """
        获取指定作用域的环境变量
        
        Args:
            scope (str): 作用域，可选值为 "system" 或 "user"
            
        Returns:
            dict: 环境变量名和值的字典
        """
        env_vars = {}
        try:
            if scope == "system":
                # 打开系统环境变量注册表
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, self.SYSTEM_ENV_REG_PATH, 0, winreg.KEY_READ)
            elif scope == "user":
                # 打开用户环境变量注册表
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.USER_ENV_REG_PATH, 0, winreg.KEY_READ)
            else:
                raise ValueError("Invalid scope. Must be 'system' or 'user'")

            # 读取所有环境变量
            i = 0
            while True:
                try:
                    name, value, _ = winreg.EnumValue(key, i)
                    env_vars[name] = value
                    i += 1
                except OSError:
                    break

            winreg.CloseKey(key)
        except Exception as e:
            print(f"Error getting environment variables: {e}")
            return {}

        return env_vars

    def add_environment_variable(self, name, value, scope):
        """
        添加环境变量
        
        Args:
            name (str): 环境变量名
            value (str): 环境变量值
            scope (str): 作用域，可选值为 "system" 或 "user"
            
        Returns:
            bool: 操作是否成功
        """
        try:
            if scope == "system":
                # 打开系统环境变量注册表，需要写权限
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, self.SYSTEM_ENV_REG_PATH, 0, winreg.KEY_SET_VALUE)
            elif scope == "user":
                # 打开用户环境变量注册表，需要写权限
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.USER_ENV_REG_PATH, 0, winreg.KEY_SET_VALUE)
            else:
                raise ValueError("Invalid scope. Must be 'system' or 'user'")

            # 设置环境变量
            winreg.SetValueEx(key, name, 0, winreg.REG_EXPAND_SZ, value)
            winreg.CloseKey(key)

            # 通知系统环境变量已更改
            self._notify_system()
            return True
        except Exception as e:
            print(f"Error adding environment variable: {e}")
            return False

    def update_environment_variable(self, name, value, scope):
        """
        更新环境变量
        
        Args:
            name (str): 环境变量名
            value (str): 新的环境变量值
            scope (str): 作用域，可选值为 "system" 或 "user"
            
        Returns:
            bool: 操作是否成功
        """
        # 更新操作与添加操作相同，因为SetValueEx会覆盖已存在的值
        return self.add_environment_variable(name, value, scope)

    def delete_environment_variable(self, name, scope):
        """
        删除环境变量
        
        Args:
            name (str): 环境变量名
            scope (str): 作用域，可选值为 "system" 或 "user"
            
        Returns:
            bool: 操作是否成功
        """
        try:
            if scope == "system":
                # 打开系统环境变量注册表，需要写权限
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, self.SYSTEM_ENV_REG_PATH, 0, winreg.KEY_SET_VALUE)
            elif scope == "user":
                # 打开用户环境变量注册表，需要写权限
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.USER_ENV_REG_PATH, 0, winreg.KEY_SET_VALUE)
            else:
                raise ValueError("Invalid scope. Must be 'system' or 'user'")

            # 删除环境变量
            winreg.DeleteValue(key, name)
            winreg.CloseKey(key)

            # 通知系统环境变量已更改
            self._notify_system()
            return True
        except Exception as e:
            print(f"Error deleting environment variable: {e}")
            return False

    def _notify_system(self):
        """
        通知系统环境变量已更改
        """
        try:
            import ctypes
            # 发送WM_SETTINGCHANGE消息通知系统
            ctypes.windll.user32.SendMessageW(0xFFFF, 0x001A, 0, "Environment")
        except Exception as e:
            print(f"Error notifying system: {e}")

if __name__ == "__main__":
    # 测试代码
    manager = EnvironmentVariableManager()
    
    # 获取用户环境变量
    user_vars = manager.get_environment_variables("user")
    print("User environment variables:")
    for name, value in user_vars.items():
        print(f"{name}: {value}")
    
    # 获取系统环境变量
    system_vars = manager.get_environment_variables("system")
    print("\nSystem environment variables:")
    for name, value in system_vars.items():
        print(f"{name}: {value}")
