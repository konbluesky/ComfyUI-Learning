import os
from pathlib import Path

def get_app_data_dir():
    """获取应用程序数据目录"""
    home = str(Path.home())
    app_dir = os.path.join(home, '.comfy-service')
    
    # 确保目录存在
    if not os.path.exists(app_dir):
        os.makedirs(app_dir)
        
    return app_dir

def get_log_dir():
    """获取日志目录"""
    log_dir = os.path.join(get_app_data_dir(), 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    return log_dir

def get_log_file(file_name):
    """获取日志文件路径"""
    return os.path.join(get_log_dir(), file_name)

def get_workflow_dir():
    """获取工作流目录"""
    workflow_dir = os.path.join(get_app_data_dir(), 'workflows')
    if not os.path.exists(workflow_dir):
        os.makedirs(workflow_dir)
    return workflow_dir

def get_workflow_path(workflow_name):
    """获取工作流文件路径"""
    workflow_path = os.path.join(get_workflow_dir(), workflow_name)
    if not os.path.exists(workflow_path):
        os.makedirs(workflow_path)
    return workflow_path

def get_log_path():
    """获取日志文件路径"""
    return os.path.join(get_log_dir(), 'app.log')

def ensure_app_dirs():
    """确保所有必要的目录都存在"""
    get_app_data_dir()  # 创建主目录
    get_log_dir()       # 创建日志目录

def load_content(path):
    """加载内容"""
    try:
        with open(path, 'r') as f:
            return f.read()
    except Exception as e:
        print(e)
        return None

if __name__ == "__main__":
    print(get_workflow_dir())
    print(get_workflow_path("first-env.json"))
    print(load_content(get_workflow_path("first-env.json")))