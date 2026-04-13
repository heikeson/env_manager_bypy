import logging
import os
from logging.handlers import RotatingFileHandler

class Logger:
    """
    日志记录类，用于记录应用程序的操作和错误信息
    """

    def __init__(self, log_dir="logs", log_file="env_manager.log", max_bytes=10*1024*1024, backup_count=5):
        """
        初始化日志记录器
        
        Args:
            log_dir (str): 日志目录
            log_file (str): 日志文件名
            max_bytes (int): 单个日志文件最大大小
            backup_count (int): 备份日志文件数量
        """
        # 创建日志目录
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # 日志文件路径
        self.log_path = os.path.join(log_dir, log_file)

        # 创建日志记录器
        self.logger = logging.getLogger("EnvironmentManager")
        self.logger.setLevel(logging.DEBUG)

        # 清除现有处理器
        if self.logger.handlers:
            self.logger.handlers.clear()

        # 创建格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # 创建文件处理器（带轮转）
        file_handler = RotatingFileHandler(
            self.log_path,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        # 添加处理器到日志记录器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def debug(self, message):
        """
        记录调试级别的日志
        
        Args:
            message (str): 日志消息
        """
        self.logger.debug(message)

    def info(self, message):
        """
        记录信息级别的日志
        
        Args:
            message (str): 日志消息
        """
        self.logger.info(message)

    def warning(self, message):
        """
        记录警告级别的日志
        
        Args:
            message (str): 日志消息
        """
        self.logger.warning(message)

    def error(self, message):
        """
        记录错误级别的日志
        
        Args:
            message (str): 日志消息
        """
        self.logger.error(message)

    def critical(self, message):
        """
        记录严重错误级别的日志
        
        Args:
            message (str): 日志消息
        """
        self.logger.critical(message)

# 创建全局日志实例
logger = Logger()

if __name__ == "__main__":
    # 测试代码
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
