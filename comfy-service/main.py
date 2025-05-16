import uvicorn
from logger import Logger, app_logger as logger
import config as global_config
from web import create_app
from comfy_api import create_router
from health_check import start_health_check
import paths

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

def main():
    Logger.setup(False)

    """创建FastAPI应用"""
    app = FastAPI(
        title="DevComfy",
        description="DevComfy",
        version="1.0.0",
        docs_url=None,
        redoc_url=None
    )

    # 添加CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # 初始化日志
    Logger.setup(False)
    
    # 创建FastAPI应用
    create_app(app)
    
    # 添加comfy_api路由
    app.include_router(create_router())
    
    # 启动健康检查
    start_health_check()
    logger.info("健康检查服务已启动")
    
    # 启动服务
    logger.info(f"启动服务: {global_config.SERVICE_PORT}")
    logger.info(f"项目目录: {paths.get_app_dir()}")
    # dev model
    # uvicorn.run("app", host="0.0.0.0", port=global_config.SERVER_PORT, reload=True)
    uvicorn.run(app, host="0.0.0.0", port=global_config.SERVICE_PORT)

if __name__ == "__main__":
    main()
