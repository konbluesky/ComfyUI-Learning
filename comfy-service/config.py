import os
from pathlib import Path

from dotenv import load_dotenv

# 获取当前文件所在目录的绝对路径
current_dir = Path(__file__).resolve().parent
# 加载.env文件中的环境变量
load_dotenv(dotenv_path=current_dir / '.env')

COMFY_HOST = os.getenv("COMFY_HOST", "http://host.docker.internal:8000")

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
SERVICE_PORT = int(os.getenv("SERVICE_PORT", 8101))

# Logdy配置
LOGDY_SERVER = os.getenv("LOGDY_SERVER", "logdy")
LOGDY_PORT = int(os.getenv("LOGDY_PORT", 10800))
LOGDY_API_KEY = os.getenv("LOGDY_API_KEY", "mypassword")
