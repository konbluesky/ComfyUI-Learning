import orjson
import traceback
from datetime import datetime, timedelta, UTC
from typing import Dict, Any

import jwt
from fastapi import FastAPI, Depends, HTTPException, status, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from logger import Logger, app_logger as logger
from pydantic import BaseModel, Field

import config as global_config
from models import Token

# JWT相关函数
def create_access_token(data: dict, expires_delta: timedelta = None):
    """创建JWT token"""
    to_encode = data.copy()
    expire = datetime.now(UTC) + (expires_delta or timedelta(minutes=global_config.JWT_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, global_config.JWT_SECRET, algorithm=global_config.JWT_ALGORITHM)
    logger.info(f"创建JWT token: {encoded_jwt[:10]}...")
    return encoded_jwt

async def get_current_user(request: Request):
    """验证JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="登录凭证过期，请重新登录",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = request.cookies.get("access_token")
        if not token:
            raise credentials_exception

        try:
            payload = jwt.decode(token, global_config.JWT_SECRET, algorithms=[global_config.JWT_ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
            return username
        except jwt.InvalidTokenError as e:
            logger.error(f"JWT解码失败: {str(e)}")
            raise credentials_exception
    except Exception as e:
        logger.error(f"认证过程发生异常: {str(e)}")
        raise credentials_exception

# 登录页面HTML
LOGIN_HTML = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Comfy服务</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f7f9;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .login-container {
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            padding: 30px;
            width: 350px;
        }
        h1 {
            color: #333;
            margin-bottom: 24px;
            text-align: center;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #555;
            font-weight: bold;
        }
        input {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 16px;
            box-sizing: border-box;
        }
        button {
            background-color: #4a6cf7;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 12px;
            width: 100%;
            font-size: 16px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        button:hover {
            background-color: #3a5bd9;
        }
        .error-message {
            color: red;
            text-align: center;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <h1>Comfy Node Manager</h1>
        <form action="/login" method="post">
            <div class="form-group">
                <label for="username">用户名</label>
                <input type="text" id="username" name="username" placeholder="请输入用户名" required>
            </div>
            <div class="form-group">
                <label for="password">密码</label>
                <input type="password" id="password" name="password" placeholder="请输入密码" required>
            </div>
            <button type="submit">登录</button>
        </form>
    </div>
</body>
</html>
"""

def create_app() -> FastAPI:
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

    # 路由处理函数
    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    async def root_redirect():
        """将根路径重定向到登录页面"""
        return HTMLResponse(content='<meta http-equiv="refresh" content="0;url=/login">')

    @app.get("/login", response_class=HTMLResponse, include_in_schema=False)
    async def login_page():
        """返回登录页面HTML"""
        return HTMLResponse(content=LOGIN_HTML)

    @app.post("/login", include_in_schema=False)
    async def handle_login(request: Request):
        """处理登录表单提交"""
        form_data = await request.form()
        username = form_data.get("username")
        password = form_data.get("password")

        if not username or not password:
            return HTMLResponse(
                content=LOGIN_HTML.replace("</form>", '<div class="error-message">请输入用户名和密码</div></form>'),
                status_code=400
            )

        if username != global_config.API_USERNAME or password != global_config.API_PASSWORD:
            return HTMLResponse(
                content=LOGIN_HTML.replace("</form>", '<div class="error-message">用户名或密码错误</div></form>'),
                status_code=401
            )

        access_token = create_access_token(data={"sub": username})
        response = HTMLResponse(content=f'<meta http-equiv="refresh" content="0;url={global_config.SWAGGER_URL}">')
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=global_config.JWT_EXPIRE_MINUTES * 60
        )
        return response

    @app.post("/token", response_model=Token, include_in_schema=False)
    async def login(form_data: OAuth2PasswordRequestForm = Depends()):
        """获取访问令牌"""
        if form_data.username != global_config.API_USERNAME or form_data.password != global_config.API_PASSWORD:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token = create_access_token(data={"sub": form_data.username})
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": global_config.JWT_EXPIRE_MINUTES * 60
        }

    @app.get("/openapi.json", dependencies=[Depends(get_current_user)], include_in_schema=False)
    async def get_open_api_endpoint():
        """获取OpenAPI架构"""
        return JSONResponse(get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes
        ))

    @app.get(global_config.SWAGGER_URL, dependencies=[Depends(get_current_user)], include_in_schema=False)
    async def get_swagger_ui():
        """自定义Swagger UI端点"""
        return get_swagger_ui_html(
            openapi_url="/openapi.json",
            title=f"{app.title} - Swagger UI",
            oauth2_redirect_url=None,
            swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
            swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
        )

    @app.get(global_config.REDOC_URL, dependencies=[Depends(get_current_user)], include_in_schema=False)
    async def get_redoc_ui():
        """自定义ReDoc端点"""
        return get_redoc_html(
            openapi_url="/openapi.json",
            title=f"{app.title} - ReDoc",
            redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js",
        )

    @app.get("/api/config", dependencies=[Depends(get_current_user)], name="获取配置")
    async def get_config():
        """获取配置信息"""
        return orjson.loads(global_config.config_to_json())

    @app.post("/api/config", dependencies=[Depends(get_current_user)], name="更新配置")
    async def update_config(data: Dict[str, Any] = Body(
        ...,
        description="配置参数",
        examples=[{
            "name": "更新交易参数",
            "value": {
                "trading": {
                    "capital": {
                        "total_usdt": 2000
                    },
                    "risk": {
                        "min_funding_rate_diff": 0.0002
                    }
                }
            }
        }]
    )):
        """更新配置信息"""
        try:
            global_config.update_config(data)
            return orjson.loads(global_config.config_to_json())
        except Exception as e:
            logger.error(f"更新配置失败: {str(e)}")
            logger.error(f"错误堆栈: {traceback.format_exc()}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"更新配置失败: {str(e)}"
            )

    return app

if __name__ == "__main__":
    import uvicorn
    Logger.setup(True)
    logger.info(f"启动服务: {global_config.SERVER_PORT}")
    uvicorn.run('web:create_app', host="0.0.0.0", port=global_config.SERVER_PORT,reload=True)
