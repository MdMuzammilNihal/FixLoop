from backend.api.schemas.models import IDERequest
from fastapi.responses import JSONResponse
import time
import traceback
from backend.api.services.logic_services import analyze_code, fix_code, fix_code_self_correcting, optimize_code, execute_python_code, extract_line_info_from_error

async def process_ide_request(request: IDERequest):
    start_time = time.time()
    try:
        is_valid, errors = IDERequest.validate_request(request)
        if not is_valid:
            return JSONResponse(
                status_code=400,
                content={"errors": errors}
            )
        result = {
            "original_code": request.code,
            "ide_specific": {
                "ide_type": request.ide_type,
                "file_path": request.file_path,
                "line_number": request.line_number,
                "session_id": request.session_id
            },
            "inline_diagnostics": []
        }
        if request.action == "analyze":
            analysis_results = await analyze_code(request.code, request.language)
            result.update({
                "explanation": analysis_results.get("code_summary") or analysis_results.get("raw"),
                "errors": analysis_results.get("errors", []),
                "warnings": analysis_results.get("warnings", []),
                "hints": analysis_results.get("suggestions", [])
            })
            if analysis_results.get("errors"):
                for error in analysis_results.get("errors", []):
                    line_info = extract_line_info_from_error(error, request.code)
                    result["inline_diagnostics"].append({
                        "message": error,
                        "severity": "error",
                        "line": line_info.get("line", 1),
                        "column": line_info.get("column", 1),
                        "source": "FixLoop"
                    })
        elif request.action == "fix":
            fix_results = await fix_code_self_correcting(request.code, request.language)
            result.update({
                "processed_code": fix_results.get("fixed_code"),
                "explanation": fix_results.get("explanation")
            })
        elif request.action == "optimize":
            optimize_results = await optimize_code(request.code, request.language)
            result.update({
                "processed_code": optimize_results.get("optimized_code"),
                "explanation": optimize_results.get("explanation"),
                "performance_metrics": optimize_results.get("performance_metrics")
            })
        elif request.action == "execute":
            if request.language == "python":
                execution_results = await execute_python_code(request.code, request.inputs)
                stderr = execution_results.get("stderr", "")
                failed = execution_results.get("exit_code") not in (0, None)
                result.update({
                    "execution_result": execution_results,
                    "errors": [stderr] if failed and stderr else []
                })
            else:
                result.update({
                    "errors": [f"Execution not supported for language: {request.language}"]
                })
        result["processing_time"] = time.time() - start_time
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "original_code": request.code,
                "errors": [str(e)],
                "processing_time": time.time() - start_time
            }
        ) 