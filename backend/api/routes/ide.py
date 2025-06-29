from fastapi import APIRouter
from fastapi.responses import JSONResponse
from backend.api.schemas.models import IDERequest
from backend.api.services.ide_services import process_ide_request

router = APIRouter()

@router.post("/api/ide/analyze")
async def ide_analyze_endpoint(request: IDERequest):
    return await process_ide_request(request) 