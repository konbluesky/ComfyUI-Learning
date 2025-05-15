import os
import time
import json
import psutil
import redis
import threading
import GPUtil
import config as global_config
from logger import app_logger as logger

redis_client = redis.Redis(
    host=global_config.REDIS_HOST,
    port=global_config.REDIS_PORT,
    db=global_config.REDIS_DB,
    password=global_config.REDIS_PASSWORD,
    decode_responses=True
)

NODE_STATUS_KEY = f"comfy:node:status:{global_config.SERVICE_HOST}:{global_config.SERVICE_PORT}"

def get_system_metrics():
    """获取系统指标"""
    try:
        # CPU使用率
        cpu_usage = psutil.cpu_percent(interval=1)
        
        # GPU使用率
        gpu_usage = 0.0
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu_usage = sum(gpu.load * 100 for gpu in gpus) / len(gpus)
        except Exception as e:
            logger.error(f"Error getting GPU metrics: {e}")
        
        return {
            "host": global_config.SERVICE_HOST,
            "port": global_config.SERVICE_PORT,
            "cpu_usage": cpu_usage,
            "gpu_usage": gpu_usage,
            "last_update": int(time.time())
        }
    except Exception as e:
        logger.error(f"Error getting system metrics: {e}")
        return None

def update_node_status():
    """更新节点状态到Redis"""
    while True:
        try:
            metrics = get_system_metrics()
            if metrics:
                redis_client.set(
                    NODE_STATUS_KEY,
                    json.dumps(metrics),
                    ex=60  # 60秒过期
                )
        except Exception as e:
            logger.error(f"Error updating node status: {e}")
        
        time.sleep(5)  # 每10秒更新一次

def start_health_check():
    """启动健康检查线程"""
    thread = threading.Thread(target=update_node_status, daemon=True)
    thread.start()
    return thread
