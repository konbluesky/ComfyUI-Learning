import uvicorn
from logger import Logger, app_logger as logger
import config as global_config
from web import create_app
from comfy_api import create_router
from health_check import start_health_check


def main():
    # 初始化日志
    Logger.setup(False)
    
    # 创建FastAPI应用
    app = create_app()
    
    # 添加comfy_api路由
    app.include_router(create_router())
    
    # 启动健康检查
    start_health_check()
    logger.info("健康检查服务已启动")
    
    # 启动服务
    logger.info(f"启动服务: {global_config.SERVER_PORT}")
    # dev model
    # uvicorn.run("app", host="0.0.0.0", port=global_config.SERVER_PORT, reload=True)
    uvicorn.run(app, host="0.0.0.0", port=global_config.SERVER_PORT)

if __name__ == "__main__":
    main()
