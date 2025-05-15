import os
import traceback
import uuid

import httpx
import orjson
from fastapi import APIRouter, HTTPException

import config as global_config
import paths
from logger import app_logger as logger
from models import GenerateRequest, GenerateResponse, PromptRequest, PromptResponse


def create_router() -> APIRouter:
    """Create Comfy API router"""
    router = APIRouter(prefix="/api", tags=["Comfy API"])

    def get_host():
        return global_config.COMFY_HOST

    @router.get("/node/status", name="Get the status of the current node")
    async def comfy_status():
        url = f"{get_host()}/system_stats"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            return response.json()

    @router.get("/node/history", name="Get the history of the current node")
    async def comfy_history(isShowDetail: bool = True):
        url = f"{get_host()}/history"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if not isShowDetail:
                historyIds = [history for history in response.json().keys()]
                return historyIds
            return response.json()

    @router.get("/node/stop", name="Stop the current workflow")
    async def stop_all():
        url = f"{get_host()}/interrupt"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            return response.json()

    @router.get("/node/view", name="View the current workflow")
    async def view_image(task_id: str):
        url = f"{get_host()}/history/{task_id}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            return response.json()

    @router.get("/task/{task_id}", name="Get the status of the task")
    async def get_task_status(task_id: str):
        url = f"{get_host()}/history/{task_id}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            res_json = response.json()
            if response.status_code == 200 and res_json == {}:
                return PromptResponse(status="pending", message="Task has been uncompleted.")
            elif response.status_code == 200 and res_json != {}:
                result = res_json[task_id]
                images = next(iter(result['outputs'].values()))['images']
                return PromptResponse(status="success", message="Task has been completed.", images=images)
            else:
                return {"status": "error", "message": "Task has been failed."}

    @router.post("/generate", name="Generate image")
    async def generate(request: GenerateRequest) -> GenerateResponse:
        try:
            client_id = uuid.uuid4()
            workflow_name = request.workflow_name
            workflow_path = paths.get_workflow_path(workflow_name + ".json")
            workflow_api_path = paths.get_workflow_path(workflow_name + "-api.json")

            if not os.path.exists(workflow_path):
                raise HTTPException(status_code=404, detail="the workflow file not found")
            workflow_content = orjson.loads(paths.load_content(workflow_path))
            workflow_api_content = orjson.loads(paths.load_content(workflow_api_path))

            prompt = PromptRequest(client_id=str(client_id), prompt=workflow_api_content,
                                   extra_data={
                                       "extra_pnginfo": {
                                           "workflow": workflow_content
                                       }
                                   })

            url = f"{get_host()}/prompt"
            headers = httpx.Headers({"Content-Type": "application/json"})
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=prompt.model_dump(), headers=headers)
                logger.debug(f"{response.json()}")
                response_json = response.json()
                return GenerateResponse(task_id=response_json["prompt_id"])
        except Exception as e:
            logger.error(f"generate image failed: {e}")
            logger.error(f"error stack: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail="generate image failed")

    @router.get("/workflow/{workflow_name}", name="Get the workflow data")
    async def get_workflow(workflow_name: str):
        workflow_path = paths.get_workflow_path(workflow_name + ".json")
        if not os.path.exists(workflow_path):
            raise HTTPException(status_code=404, detail="the workflow file not found")
        return orjson.loads(paths.load_content(workflow_path))

    return router
