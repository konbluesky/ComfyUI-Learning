from pydantic import BaseModel
from typing import Optional,Dict,Any,List

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class GenerateResponse(BaseModel):
    task_id: str

class PromptRequest(BaseModel):
    client_id: str
    prompt: Dict[str,Any]
    extra_data: Dict[str,Any]


class PromptResponse(BaseModel):
    status:str
    message:str
    images:Optional[List[Dict[str,Any]]]
    

class GenerateRequest(BaseModel):
    prompt: Optional[str] = None
    workflow_name: str
