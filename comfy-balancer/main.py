import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import redis
import json
import httpx
from typing import Dict, List
import time
from pydantic import BaseModel
from typing import Optional
from logger import Logger, app_logger as logger
from web import create_app

Logger.setup(False)

app = FastAPI(title="Comfy Balancer")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SERVICE_PORT = int(os.getenv("SERVICE_PORT", 7999))
# Redis配置
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
REDIS_DB = int(os.getenv("REDIS_DB", 0))

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD,
    decode_responses=True
)

# 节点状态键前缀
NODE_STATUS_KEY = "comfy:node:status:"
NODE_QUEUE_KEY = "comfy:node:queue:"

class NodeStatus(BaseModel):
    host: str
    port: int
    cpu_usage: float
    gpu_usage: float
    last_update: float
    is_healthy: Optional[bool] = None

class QueueItem(BaseModel):
    """队列项模型"""
    client_id: str
    prompt_id: str
    timestamp: float
    status: str = "waiting"  # waiting, processing, completed, failed

class TaskStatus(BaseModel):
    """任务状态模型"""
    task_id: str
    client_id: str
    node: str
    status: str = "pending"  # pending, success, error
    message: str = ""
    images: Optional[List[str]] = None
    timestamp: float

def get_available_nodes() -> List[NodeStatus]:
    """获取所有可用节点的状态"""
    nodes = []
    for key in redis_client.keys(f"{NODE_STATUS_KEY}*"):
        node_data = redis_client.get(key)
        if node_data:
            try:
                node = NodeStatus(**json.loads(node_data))
                # 检查节点是否健康（10秒内更新过）
                if time.time() - node.last_update < 10:
                    node.is_healthy = True
                    nodes.append(node)
                else:
                    node.is_healthy = False
            except Exception as e:
                logger.error(f"Error parsing node data: {e}")
    return nodes

def select_best_node(nodes: List[NodeStatus]) -> NodeStatus:
    """根据负载均衡策略选择最佳节点"""
    if not nodes:
        raise HTTPException(status_code=503, detail="No available nodes")
    
    # 首先过滤出健康的节点
    healthy_nodes = [node for node in nodes if node.is_healthy]
    if not healthy_nodes:
        raise HTTPException(status_code=503, detail="No healthy nodes available")
    
    # 使用加权评分系统
    # GPU使用率权重为0.7，CPU使用率权重为0.3
    best_node = min(
        healthy_nodes,
        key=lambda x: (x.gpu_usage * 0.7 + x.cpu_usage * 0.3)
    )
    return best_node

async def forward_request(node: NodeStatus, path: str, method: str, data: dict = None) -> httpx.Response:
    """转发请求到选定的节点"""
    async with httpx.AsyncClient() as client:
        url = f"http://{node.host}:{node.port}/api{path}"  # 添加 /api 前缀
        try:
            if method.upper() == "GET":
                response = await client.get(url)
            elif method.upper() == "POST":
                response = await client.post(url, json=data)
            else:
                raise HTTPException(status_code=405, detail="Method not allowed")
            return response
        except Exception as e:
            logger.error(f"Error forwarding request to {url}: {e}")
            raise HTTPException(status_code=502, detail="Error forwarding request")

@app.get("/health")
async def health_check():
    """健康检查接口"""
    try:
        nodes = get_available_nodes()
        return {"status": "healthy", "nodes": nodes}
    except Exception as e:
        logger.error(f"Error in health check: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/queue/status/{prompt_id}")
async def get_queue_status(prompt_id: str):
    """获取队列中提示词的状态"""
    try:
        # 遍历所有节点查找提示词
        for node in get_available_nodes():
            queue_key = f"{NODE_QUEUE_KEY}{node.host}:{node.port}:{prompt_id}"
            item_data = redis_client.get(queue_key)
            if item_data:
                queue_item = QueueItem(**json.loads(item_data))
                return {
                    "status": queue_item.status,
                    "node": f"{node.host}:{node.port}",
                    "timestamp": queue_item.timestamp
                }
        raise HTTPException(status_code=404, detail="Prompt not found in queue")
    except Exception as e:
        logger.error(f"Error getting queue status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate")
async def generate_image(data: dict):
    """生成图片请求"""
    try:
        logger.info(f"/api/generate params: {data}")
        client_id = data.get("client_id", str(time.time()))
        
        # 获取可用节点
        nodes = get_available_nodes()
        if not nodes:
            raise HTTPException(status_code=503, detail="No available nodes")
        
        # 选择最佳节点
        best_node = select_best_node(nodes)
        
        # 转发请求到选定的节点
        response = await forward_request(
            best_node,
            "/generate",
            "POST",
            data
        )
        
        response_data = response.json()
        task_id = response_data.get("task_id")
        
        # 记录任务状态
        task_status = TaskStatus(
            task_id=task_id,
            client_id=client_id,
            node=f"{best_node.host}:{best_node.port}",
            timestamp=time.time()
        )
        
        # 将任务状态写入Redis
        task_key = f"comfy:task:{task_id}"
        redis_client.set(task_key, task_status.json(), ex=3600)  # 1小时过期
        
        return response_data
    except Exception as e:
        logger.error(f"Error generating image: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/task/{task_id}")
async def get_task_status(task_id: str):
    """获取任务状态"""
    try:
        # 首先从Redis获取任务信息
        task_key = f"comfy:task:{task_id}"
        task_data = redis_client.get(task_key)
        
        if not task_data:
            raise HTTPException(status_code=404, detail="Task not found")
        
        task_status = TaskStatus(**json.loads(task_data))
        
        # 从对应节点获取最新状态
        node_host, node_port = task_status.node.split(":")
        node = NodeStatus(
            host=node_host,
            port=int(node_port),
            cpu_usage=0,
            gpu_usage=0,
            last_update=time.time()
        )
        
        response = await forward_request(
            node,
            f"/task/{task_id}",
            "GET"
        )
        
        # 更新任务状态
        response_data = response.json()
        task_status.status = response_data.get("status", "pending")
        task_status.message = response_data.get("message", "")
        task_status.images = response_data.get("images", [])
        
        # 更新Redis中的状态
        redis_client.set(task_key, task_status.json(), ex=3600)
        
        return response_data
    except Exception as e:
        logger.error(f"Error getting task status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    create_app(app)
    uvicorn.run(app, host="0.0.0.0", port=SERVICE_PORT) 