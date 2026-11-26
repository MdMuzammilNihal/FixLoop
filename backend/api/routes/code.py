from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, StreamingResponse
from backend.api.schemas.models import CodeRequest, CodeResponse, BatchCodeRequest, ContextAwareFixRequest, ChatRequest
from backend.api.services.code_services import (
    process_code,
    process_code_stream,
    process_code_batch,
    fix_code_with_context,
    process_chat
)

router = APIRouter()

@router.post("/api/code")
async def code_endpoint(request: CodeRequest):
    return await process_code(request)

@router.post("/api/code/stream")
async def code_stream_endpoint(request: CodeRequest):
    return await process_code_stream(request)

@router.post("/api/code/batch")
async def code_batch_endpoint(request: BatchCodeRequest):
    return await process_code_batch(request)

@router.post("/api/code/fix-with-context")
async def code_fix_with_context_endpoint(request: ContextAwareFixRequest):
    return await fix_code_with_context(request) 

@router.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    return await process_chat(request)
