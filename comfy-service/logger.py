from loguru import logger
from datetime import datetime
import paths 


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
