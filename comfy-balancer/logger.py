from loguru import logger
import os
from datetime import datetime
import socket

LOGDY_SERVER = os.getenv("LOGDY_SERVER", "localhost")
LOGDY_PORT = int(os.getenv("LOGDY_PORT", 10800))
LOGDY_API_KEY = os.getenv("LOGDY_API_KEY", "mypassword")
SERVICE_HOST = os.getenv("SERVICE_HOST", "comfy_balancer")

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
        # # 清除默认的处理器
        # if debug:
        #     logger.remove()

        try:
            logger.add(TCPLoguruHandler(host=LOGDY_PORT, port=LOGDY_PORT), format="{time} {level} "+ SERVICE_HOST+" {message} ", level=f"{log_level}")
        except Exception as e:
            logger.error(f"Failed to add TCPLoguruHandler: {e}")

        try:
            logger.add(TCPLoguruHandler(host=LOGDY_SERVER, port=LOGDY_PORT), format="{time} {level} "+ SERVICE_HOST+" {message} ", level="ERROR")
        except Exception as e:
            logger.error(f"Failed to add TCPLoguruHandler: {e}")


app_logger = logger
