from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    session_id: str


class ChatResponse(BaseModel):
    response: str
    session_id: str


class ClearRequest(BaseModel):
    session_id: str


class ClearResponse(BaseModel):
    message: str
    session_id: str
