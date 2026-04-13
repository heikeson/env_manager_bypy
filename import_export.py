import json
import os
from env_manager import EnvironmentVariableManager
from logger import logger

class ImportExportManager:
    """
    导入导出管理类，用于环境变量的导入和导出
    """

    def __init__(self):
        """
        初始化导入导出管理器
        """
        self.env_manager = EnvironmentVariableManager()

    def export_environment_variables(self, scope, format, file_path):
        """
        导出环境变量
        
        Args:
            scope (str): 作用域，可选值为 "system"、"user" 或 "all"
            format (str): 格式，可选值为 "json" 或 "text"
            file_path (str): 导出文件路径
            
        Returns:
            bool: 操作是否成功
        """
        try:
            export_data = {}

            # 根据作用域获取环境变量
            if scope == "system" or scope == "all":
                system_vars = self.env_manager.get_environment_variables("system")
                if system_vars:
                    export_data["system"] = system_vars

            if scope == "user" or scope == "all":
                user_vars = self.env_manager.get_environment_variables("user")
                if user_vars:
                    export_data["user"] = user_vars

            # 根据格式导出
            if format == "json":
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)
            elif format == "text":
                with open(file_path, 'w', encoding='utf-8') as f:
                    if "system" in export_data:
                        f.write("=== System Environment Variables ===\n")
                        for name, value in export_data["system"].items():
                            f.write(f"{name}={value}\n")
                        f.write("\n")
                    if "user" in export_data:
                        f.write("=== User Environment Variables ===\n")
                        for name, value in export_data["user"].items():
                            f.write(f"{name}={value}\n")
            else:
                logger.error(f"Invalid format: {format}")
                return False

            logger.info(f"Successfully exported environment variables to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error exporting environment variables: {e}")
            return False

    def import_environment_variables(self, file_path, scope, overwrite):
        """
        导入环境变量
        
        Args:
            file_path (str): 导入文件路径
            scope (str): 作用域，可选值为 "system" 或 "user"
            overwrite (bool): 是否覆盖现有环境变量
            
        Returns:
            bool: 操作是否成功
        """
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 尝试解析为JSON
            try:
                import_data = json.loads(content)
                # 从JSON数据中获取对应作用域的环境变量
                if scope in import_data:
                    env_vars = import_data[scope]
                else:
                    logger.error(f"No {scope} environment variables found in the file")
                    return False
            except json.JSONDecodeError:
                # 如果不是JSON格式，尝试解析为文本格式
                env_vars = {}
                lines = content.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and '=' in line and not line.startswith('#') and not line.startswith('==='):
                        name, value = line.split('=', 1)
                        env_vars[name.strip()] = value.strip()

            # 导入环境变量
            success_count = 0
            failure_count = 0

            for name, value in env_vars.items():
                # 检查是否已存在
                existing_vars = self.env_manager.get_environment_variables(scope)
                if name in existing_vars:
                    if overwrite:
                        # 覆盖现有环境变量
                        if self.env_manager.update_environment_variable(name, value, scope):
                            success_count += 1
                        else:
                            failure_count += 1
                    else:
                        # 跳过已存在的环境变量
                        logger.info(f"Skipped existing environment variable: {name}")
                else:
                    # 添加新环境变量
                    if self.env_manager.add_environment_variable(name, value, scope):
                        success_count += 1
                    else:
                        failure_count += 1

            logger.info(f"Import completed: {success_count} success, {failure_count} failure")
            return success_count > 0
        except Exception as e:
            logger.error(f"Error importing environment variables: {e}")
            return False

if __name__ == "__main__":
    # 测试代码
    import_export = ImportExportManager()
    
    # 测试导出到JSON
    export_json_path = "env_vars.json"
    import_export.export_environment_variables("all", "json", export_json_path)
    print(f"Exported to JSON: {export_json_path}")
    
    # 测试导出到文本
    export_text_path = "env_vars.txt"
    import_export.export_environment_variables("all", "text", export_text_path)
    print(f"Exported to text: {export_text_path}")
    
    # 测试导入（注意：这里只是测试，不会实际导入）
    # import_export.import_environment_variables(export_json_path, "user", False)
