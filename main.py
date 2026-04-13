#!/usr/bin/env python3
"""
环境变量管理器主入口文件
"""

from src.gui import EnvironmentManagerGUI
import wx

if __name__ == "__main__":
    """
    主函数
    """
    # 启动应用程序
    app = wx.App()
    frame = EnvironmentManagerGUI(None, "环境变量管理器")
    app.MainLoop()
