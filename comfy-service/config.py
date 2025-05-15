
import os
from types import SimpleNamespace
from dotenv import load_dotenv
from pathlib import Path
# 获取当前文件所在目录的绝对路径
current_dir = Path(__file__).resolve().parent
# 加载.env文件中的环境变量
load_dotenv(dotenv_path=current_dir / '.env')

SERVER_PORT=8101
COMFY_HOST = "http://127.0.0.1:8000"

# API文档路径
SWAGGER_URL = "/a/s"
REDOC_URL = "/a/r"
LOGIN_URL = "/login"
# API认证信息
API_USERNAME = os.getenv("API_USERNAME")
API_PASSWORD = os.getenv("API_PASSWORD") 

# JWT配置
JWT_SECRET = os.getenv("JWT_SECRET", "test-dev-secret-key")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 3000


# Redis配置
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

# 服务配置
SERVICE_HOST = os.getenv("SERVICE_HOST", "localhost")
SERVICE_PORT = int(os.getenv("SERVICE_PORT", 8188))

def config_to_json():
    """
    将配置转换为JSON格式
    """
    import types
    import orjson
    """
    将配置转换为JSON格式，处理不可序列化的对象，使用orjson提高性能
    """
    config_dict = {}
    for key, value in globals().items():
        # 排除私有变量、模块和函数
        if not key.startswith('_') and not isinstance(value, (types.ModuleType, types.FunctionType)):
            try:
                # 尝试转换为可JSON序列化的格式
                if isinstance(value, type) or hasattr(value, '__dict__'):
                    # 处理自定义类和命名空间
                    if hasattr(value, '__dict__'):
                        config_dict[key] = {k: v for k, v in value.__dict__.items() 
                                          if not k.startswith('_')}
                    else:
                        config_dict[key] = str(value)
                elif isinstance(value, (list, tuple)):
                    # 处理列表和元组
                    config_dict[key] = [str(item) if not isinstance(item, (int, float, str, bool, type(None))) 
                                       else item for item in value]
                elif isinstance(value, dict):
                    # 处理字典
                    temp_dict = {}
                    for k, v in value.items():
                        if isinstance(v, (int, float, str, bool, type(None))):
                            temp_dict[k] = v
                        else:
                            temp_dict[k] = str(v)
                    config_dict[key] = temp_dict
                else:
                    # 其他简单类型直接添加
                    config_dict[key] = value
            except (TypeError, ValueError):
                # 如果无法处理，则转为字符串
                config_dict[key] = str(value)
    
    # orjson.dumps返回bytes，需要解码为字符串
    return orjson.dumps(
        config_dict, 
        option=orjson.OPT_INDENT_2 | orjson.OPT_NON_STR_KEYS | orjson.OPT_SERIALIZE_NUMPY
    ).decode('utf-8')


def update_config(data:dict) -> None:
    """根据data中的配置参数更新全局配置"""
    for key, value in data.items():
        if key.upper() in globals():
            globals()[key.upper()] = value