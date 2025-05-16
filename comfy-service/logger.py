from loguru import logger
from datetime import datetime
import paths 
import socket
import config as global_config

class TCPLoguruHandler(object):
    """
        基于TCP通道发送日志到logdy平台
    """
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
    def write(self, message):
        self.sock.sendall(message.encode('utf-8'))
    def __del__(self):
        self.sock.close()

class Logger:
    @staticmethod
    def setup(debug: bool = False):
        log_level = "INFO"
        # 清除默认的处理器
        if debug:
            logger.remove()

        # 添加控制台输出
        # logger.add(
        #     sys.stderr,
        #     format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        #     level=f"{log_level}"
        # )
        try:
            logger.add(TCPLoguruHandler(host=global_config.LOGDY_SERVER, port=global_config.LOGDY_PORT), format="{time} {level} " + global_config.SERVICE_HOST +" {message}", level=f"{log_level}")
        except Exception as e:
            logger.error(f"Failed to add TCPLoguruHandler: {e}")

        # 添加异常文件输出
        logger.add(
            paths.get_log_file("error.log"),
            rotation="500 MB",
            retention="10 days",
            level="ERROR",
            encoding="utf-8"
        )

        logger.add(
            paths.get_log_file("app.log"),
            rotation="500 MB",
            retention="10 days",
            level="INFO",
            encoding="utf-8"
        )


app_logger = logger
