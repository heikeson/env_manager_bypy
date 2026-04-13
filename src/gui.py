import wx
import os
from src.env_manager import EnvironmentVariableManager
from src.security import SecurityManager
from src.import_export import ImportExportManager
from src.logger import logger

class EnvironmentManagerGUI(wx.Frame):
    """
    环境变量管理器GUI类
    """

    def __init__(self, parent, title):
        """
        初始化GUI
        
        Args:
            parent: 父窗口
            title: 窗口标题
        """
        super(EnvironmentManagerGUI, self).__init__(parent, title=title, size=(800, 600))
        
        # 初始化管理器
        self.env_manager = EnvironmentVariableManager()
        self.security = SecurityManager()
        self.import_export = ImportExportManager()
        
        # 当前选中的作用域
        self.current_scope = "user"
        
        # 创建主面板
        self.panel = wx.Panel(self)
        
        # 创建布局
        self.create_layout()
        
        # 加载环境变量
        self.load_environment_variables()
        
        # 显示窗口
        self.Center()
        self.Show()

    def create_layout(self):
        """
        创建布局
        """
        # 主垂直布局
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 作用域选择器
        scope_sizer = wx.BoxSizer(wx.HORIZONTAL)
        scope_label = wx.StaticText(self.panel, label="作用域:")
        self.scope_choice = wx.Choice(self.panel, choices=["用户", "系统"])
        self.scope_choice.SetSelection(0)  # 默认选择用户
        self.scope_choice.Bind(wx.EVT_CHOICE, self.on_scope_change)
        scope_sizer.Add(scope_label, 0, wx.ALL, 5)
        scope_sizer.Add(self.scope_choice, 0, wx.ALL, 5)
        main_sizer.Add(scope_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        # 环境变量列表
        list_sizer = wx.BoxSizer(wx.VERTICAL)
        list_label = wx.StaticText(self.panel, label="环境变量列表:")
        list_sizer.Add(list_label, 0, wx.ALL, 5)
        
        # 创建列表控件
        self.env_list = wx.ListCtrl(self.panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.env_list.InsertColumn(0, "变量名", width=200)
        self.env_list.InsertColumn(1, "值", width=500)
        self.env_list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_item_selected)
        list_sizer.Add(self.env_list, 1, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(list_sizer, 1, wx.EXPAND | wx.ALL, 10)
        
        # 操作按钮
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.add_btn = wx.Button(self.panel, label="添加")
        self.add_btn.Bind(wx.EVT_BUTTON, self.on_add)
        button_sizer.Add(self.add_btn, 0, wx.ALL, 5)
        
        self.edit_btn = wx.Button(self.panel, label="编辑")
        self.edit_btn.Bind(wx.EVT_BUTTON, self.on_edit)
        self.edit_btn.Disable()  # 初始禁用
        button_sizer.Add(self.edit_btn, 0, wx.ALL, 5)
        
        self.delete_btn = wx.Button(self.panel, label="删除")
        self.delete_btn.Bind(wx.EVT_BUTTON, self.on_delete)
        self.delete_btn.Disable()  # 初始禁用
        button_sizer.Add(self.delete_btn, 0, wx.ALL, 5)
        
        button_sizer.AddStretchSpacer()
        
        self.export_btn = wx.Button(self.panel, label="导出")
        self.export_btn.Bind(wx.EVT_BUTTON, self.on_export)
        button_sizer.Add(self.export_btn, 0, wx.ALL, 5)
        
        self.import_btn = wx.Button(self.panel, label="导入")
        self.import_btn.Bind(wx.EVT_BUTTON, self.on_import)
        button_sizer.Add(self.import_btn, 0, wx.ALL, 5)
        
        main_sizer.Add(button_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        # 设置主布局
        self.panel.SetSizer(main_sizer)

    def load_environment_variables(self):
        """
        加载环境变量到列表
        """
        # 清空列表
        self.env_list.DeleteAllItems()
        
        # 获取环境变量
        scope = "user" if self.scope_choice.GetSelection() == 0 else "system"
        self.current_scope = scope
        env_vars = self.env_manager.get_environment_variables(scope)
        
        # 添加到列表
        for name, value in env_vars.items():
            index = self.env_list.InsertItem(self.env_list.GetItemCount(), name)
            self.env_list.SetItem(index, 1, value)
        
        # 禁用编辑和删除按钮
        self.edit_btn.Disable()
        self.delete_btn.Disable()

    def on_scope_change(self, event):
        """
        作用域变更事件
        """
        self.load_environment_variables()

    def on_item_selected(self, event):
        """
        列表项选择事件
        """
        self.edit_btn.Enable()
        self.delete_btn.Enable()

    def on_add(self, event):
        """
        添加环境变量
        """
        dialog = EnvVarDialog(self, "添加环境变量")
        if dialog.ShowModal() == wx.ID_OK:
            name = dialog.name_ctrl.GetValue().strip()
            value = dialog.value_ctrl.GetValue().strip()
            
            if not name:
                wx.MessageBox("变量名不能为空", "错误", wx.OK | wx.ICON_ERROR)
                return
            
            # 检查权限
            if self.current_scope == "system" and not self.security.is_admin():
                wx.MessageBox("需要管理员权限才能修改系统环境变量", "权限不足", wx.OK | wx.ICON_ERROR)
                self.security.request_admin()
                return
            
            # 检查安全性
            if not self.security.check_environment_variable_safety(name):
                if wx.MessageBox(f"{name} 是系统关键环境变量，修改可能影响系统稳定性，确定要继续吗？", "警告", wx.YES_NO | wx.ICON_WARNING) != wx.YES:
                    return
            
            # 确认变更
            if wx.MessageBox(f"确定要添加环境变量 {name} = {value} 吗？", "确认", wx.YES_NO | wx.ICON_QUESTION) == wx.YES:
                if self.env_manager.add_environment_variable(name, value, self.current_scope):
                    wx.MessageBox("添加成功", "成功", wx.OK | wx.ICON_INFORMATION)
                    self.load_environment_variables()
                    logger.info(f"Added environment variable: {name} = {value} (scope: {self.current_scope})")
                else:
                    wx.MessageBox("添加失败", "错误", wx.OK | wx.ICON_ERROR)
                    logger.error(f"Failed to add environment variable: {name}")
        dialog.Destroy()

    def on_edit(self, event):
        """
        编辑环境变量
        """
        selected_index = self.env_list.GetFirstSelected()
        if selected_index == -1:
            return
        
        name = self.env_list.GetItemText(selected_index, 0)
        value = self.env_list.GetItemText(selected_index, 1)
        
        dialog = EnvVarDialog(self, "编辑环境变量", name, value)
        if dialog.ShowModal() == wx.ID_OK:
            new_name = dialog.name_ctrl.GetValue().strip()
            new_value = dialog.value_ctrl.GetValue().strip()
            
            if not new_name:
                wx.MessageBox("变量名不能为空", "错误", wx.OK | wx.ICON_ERROR)
                return
            
            # 检查权限
            if self.current_scope == "system" and not self.security.is_admin():
                wx.MessageBox("需要管理员权限才能修改系统环境变量", "权限不足", wx.OK | wx.ICON_ERROR)
                self.security.request_admin()
                return
            
            # 检查安全性
            if not self.security.check_environment_variable_safety(new_name):
                if wx.MessageBox(f"{new_name} 是系统关键环境变量，修改可能影响系统稳定性，确定要继续吗？", "警告", wx.YES_NO | wx.ICON_WARNING) != wx.YES:
                    return
            
            # 确认变更
            if wx.MessageBox(f"确定要修改环境变量 {name} 为 {new_name} = {new_value} 吗？", "确认", wx.YES_NO | wx.ICON_QUESTION) == wx.YES:
                # 如果名称变更，需要先删除旧的，再添加新的
                if new_name != name:
                    if self.env_manager.delete_environment_variable(name, self.current_scope):
                        if self.env_manager.add_environment_variable(new_name, new_value, self.current_scope):
                            wx.MessageBox("修改成功", "成功", wx.OK | wx.ICON_INFORMATION)
                            self.load_environment_variables()
                            logger.info(f"Updated environment variable: {name} -> {new_name} = {new_value} (scope: {self.current_scope})")
                        else:
                            # 恢复旧的环境变量
                            self.env_manager.add_environment_variable(name, value, self.current_scope)
                            wx.MessageBox("修改失败", "错误", wx.OK | wx.ICON_ERROR)
                            logger.error(f"Failed to update environment variable: {name} -> {new_name}")
                    else:
                        wx.MessageBox("修改失败", "错误", wx.OK | wx.ICON_ERROR)
                        logger.error(f"Failed to delete old environment variable: {name}")
                else:
                    # 名称不变，直接更新
                    if self.env_manager.update_environment_variable(name, new_value, self.current_scope):
                        wx.MessageBox("修改成功", "成功", wx.OK | wx.ICON_INFORMATION)
                        self.load_environment_variables()
                        logger.info(f"Updated environment variable: {name} = {new_value} (scope: {self.current_scope})")
                    else:
                        wx.MessageBox("修改失败", "错误", wx.OK | wx.ICON_ERROR)
                        logger.error(f"Failed to update environment variable: {name}")
        dialog.Destroy()

    def on_delete(self, event):
        """
        删除环境变量
        """
        selected_index = self.env_list.GetFirstSelected()
        if selected_index == -1:
            return
        
        name = self.env_list.GetItemText(selected_index, 0)
        value = self.env_list.GetItemText(selected_index, 1)
        
        # 检查权限
        if self.current_scope == "system" and not self.security.is_admin():
            wx.MessageBox("需要管理员权限才能修改系统环境变量", "权限不足", wx.OK | wx.ICON_ERROR)
            self.security.request_admin()
            return
        
        # 检查安全性
        if not self.security.check_environment_variable_safety(name):
            if wx.MessageBox(f"{name} 是系统关键环境变量，删除可能影响系统稳定性，确定要继续吗？", "警告", wx.YES_NO | wx.ICON_WARNING) != wx.YES:
                return
        
        # 确认删除
        if wx.MessageBox(f"确定要删除环境变量 {name} 吗？", "确认", wx.YES_NO | wx.ICON_QUESTION) == wx.YES:
            if self.env_manager.delete_environment_variable(name, self.current_scope):
                wx.MessageBox("删除成功", "成功", wx.OK | wx.ICON_INFORMATION)
                self.load_environment_variables()
                logger.info(f"Deleted environment variable: {name} (scope: {self.current_scope})")
            else:
                wx.MessageBox("删除失败", "错误", wx.OK | wx.ICON_ERROR)
                logger.error(f"Failed to delete environment variable: {name}")

    def on_export(self, event):
        """
        导出环境变量
        """
        # 创建文件选择对话框
        wildcard = "JSON文件 (*.json)|*.json|文本文件 (*.txt)|*.txt"
        dialog = wx.FileDialog(self, "导出环境变量", wildcard=wildcard, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        
        if dialog.ShowModal() == wx.ID_OK:
            file_path = dialog.GetPath()
            file_ext = os.path.splitext(file_path)[1].lower()
            
            # 确定导出格式
            if file_ext == ".json":
                format = "json"
            elif file_ext == ".txt":
                format = "text"
            else:
                wx.MessageBox("不支持的文件格式", "错误", wx.OK | wx.ICON_ERROR)
                return
            
            # 确定导出范围
            scope = "all"
            if self.scope_choice.GetSelection() == 0:
                scope = "user"
            else:
                scope = "system"
            
            if self.import_export.export_environment_variables(scope, format, file_path):
                wx.MessageBox(f"导出成功到 {file_path}", "成功", wx.OK | wx.ICON_INFORMATION)
                logger.info(f"Exported environment variables to {file_path}")
            else:
                wx.MessageBox("导出失败", "错误", wx.OK | wx.ICON_ERROR)
                logger.error(f"Failed to export environment variables to {file_path}")
        dialog.Destroy()

    def on_import(self, event):
        """
        导入环境变量
        """
        # 创建文件选择对话框
        wildcard = "JSON文件 (*.json)|*.json|文本文件 (*.txt)|*.txt"
        dialog = wx.FileDialog(self, "导入环境变量", wildcard=wildcard, style=wx.FD_OPEN)
        
        if dialog.ShowModal() == wx.ID_OK:
            file_path = dialog.GetPath()
            
            # 检查权限
            if self.current_scope == "system" and not self.security.is_admin():
                wx.MessageBox("需要管理员权限才能修改系统环境变量", "权限不足", wx.OK | wx.ICON_ERROR)
                self.security.request_admin()
                return
            
            # 确认覆盖
            overwrite = False
            if wx.MessageBox("是否覆盖已存在的环境变量？", "确认", wx.YES_NO | wx.ICON_QUESTION) == wx.YES:
                overwrite = True
            
            if self.import_export.import_environment_variables(file_path, self.current_scope, overwrite):
                wx.MessageBox("导入成功", "成功", wx.OK | wx.ICON_INFORMATION)
                self.load_environment_variables()
                logger.info(f"Imported environment variables from {file_path}")
            else:
                wx.MessageBox("导入失败", "错误", wx.OK | wx.ICON_ERROR)
                logger.error(f"Failed to import environment variables from {file_path}")
        dialog.Destroy()

class EnvVarDialog(wx.Dialog):
    """
    环境变量编辑对话框
    """

    def __init__(self, parent, title, name="", value=""):
        """
        初始化对话框
        
        Args:
            parent: 父窗口
            title: 对话框标题
            name: 环境变量名
            value: 环境变量值
        """
        super(EnvVarDialog, self).__init__(parent, title=title, size=(500, 300))
        
        # 创建面板
        panel = wx.Panel(self)
        
        # 创建布局
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 变量名
        name_sizer = wx.BoxSizer(wx.HORIZONTAL)
        name_label = wx.StaticText(panel, label="变量名:")
        self.name_ctrl = wx.TextCtrl(panel, value=name)
        name_sizer.Add(name_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        name_sizer.Add(self.name_ctrl, 1, wx.ALL, 5)
        sizer.Add(name_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        # 变量值
        value_sizer = wx.BoxSizer(wx.HORIZONTAL)
        value_label = wx.StaticText(panel, label="值:")
        self.value_ctrl = wx.TextCtrl(panel, value=value, style=wx.TE_MULTILINE | wx.TE_PROCESS_ENTER)
        value_sizer.Add(value_label, 0, wx.ALL | wx.ALIGN_TOP, 5)
        value_sizer.Add(self.value_ctrl, 1, wx.ALL | wx.EXPAND, 5)
        sizer.Add(value_sizer, 1, wx.EXPAND | wx.ALL, 10)
        
        # 按钮
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.AddStretchSpacer()
        
        cancel_btn = wx.Button(panel, label="取消")
        cancel_btn.Bind(wx.EVT_BUTTON, self.on_cancel)
        btn_sizer.Add(cancel_btn, 0, wx.ALL, 5)
        
        ok_btn = wx.Button(panel, label="确定")
        ok_btn.Bind(wx.EVT_BUTTON, self.on_ok)
        btn_sizer.Add(ok_btn, 0, wx.ALL, 5)
        
        sizer.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        # 设置布局
        panel.SetSizer(sizer)

    def on_ok(self, event):
        """
        确定按钮事件
        """
        self.EndModal(wx.ID_OK)

    def on_cancel(self, event):
        """
        取消按钮事件
        """
        self.EndModal(wx.ID_CANCEL)

if __name__ == "__main__":
    # 启动应用程序
    app = wx.App()
    frame = EnvironmentManagerGUI(None, "环境变量管理器")
    app.MainLoop()
