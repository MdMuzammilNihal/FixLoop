from backend.api.schemas.models import CodeRequest, CodeResponse, BatchCodeRequest, ContextAwareFixRequest
from fastapi.responses import JSONResponse, StreamingResponse
import time
import json
import traceback
from backend.api.services.logic_services import (
    analyze_code,
    optimize_code,
    fix_code,
    generate_hints,
    execute_python_code,
    build_prompt,
    estimate_max_tokens,
    check_ollama_available
)

# process_code
async def process_code(request: CodeRequest):
    start_time = time.time()
    try:
        if not CodeRequest.validate_code(request.code):
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Invalid code: Code cannot be empty",
                    "processing_time": time.time() - start_time
                }
            )
        if not CodeRequest.validate_language(request.language):
            return JSONResponse(
                status_code=400,
                content={
                    "error": f"Unsupported language: {request.language}",
                    "processing_time": time.time() - start_time
                }
            )
        if not CodeRequest.validate_action(request.action):
            return JSONResponse(
                status_code=400,
                content={
                    "error": f"Unsupported action: {request.action}",
                    "processing_time": time.time() - start_time
                }
            )
        if request.inputs is not None and not CodeRequest.validate_inputs(request.inputs):
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Invalid inputs: Inputs must be a list of strings",
                    "processing_time": time.time() - start_time
                }
            )
        # ollama_available check should be handled at a higher level or injected
        try:
            # Check Ollama for LLM-dependent actions
            if request.action in ['analyze', 'optimize', 'hint', 'fix']:
                ollama_ok = await check_ollama_available()
                if not ollama_ok:
                    return JSONResponse(
                        status_code=503,
                        content={
                            "error": "Ollama service is not available. Please ensure it is running at the configured OLLAMA_BASE_URL.",
                            "processing_time": time.time() - start_time
                        }
                    )
            if request.action == 'analyze':
                result = await analyze_code(request.code, request.language)
                explanation = result.get('code_summary') or result.get('raw') or ""
                errors = result.get('errors', [])
                warnings = result.get('warnings', [])
                suggestions = result.get('suggestions', [])
                return CodeResponse(
                    original_code=request.code,
                    explanation=explanation,
                    errors=errors if isinstance(errors, list) else [],
                    warnings=warnings if isinstance(warnings, list) else [],
                    suggestions=suggestions if isinstance(suggestions, list) else [],
                    hints=suggestions if isinstance(suggestions, list) else [],
                    processing_time=time.time() - start_time
                )
            elif request.action == 'optimize':
                result = await optimize_code(request.code, request.language)
                if isinstance(result, dict) and result.get('explanation', '').startswith('Error'):
                    return JSONResponse(
                        status_code=500,
                        content={
                            "error": result.get('explanation'),
                            "processing_time": time.time() - start_time
                        }
                    )
                optimized_code = result.get('optimized_code', '')
                explanation = result.get('explanation', '')
                return CodeResponse(
                    original_code=request.code,
                    processed_code=optimized_code,
                    explanation=explanation,
                    processing_time=time.time() - start_time
                )
            elif request.action == 'hint':
                result = await generate_hints(request.code, request.language)
                if isinstance(result, dict) and result.get('hints') and result['hints'][0].startswith('Error'):
                    return JSONResponse(
                        status_code=500,
                        content={
                            "error": result.get('hints'),
                            "processing_time": time.time() - start_time
                        }
                    )
                hints = result.get('hints', [])
                return CodeResponse(
                    original_code=request.code,
                    hints=hints,
                    processing_time=time.time() - start_time
                )
            elif request.action == 'fix':
                result = await fix_code(request.code, request.language)
                if isinstance(result, dict) and result.get('explanation', '').startswith('Error'):
                    return JSONResponse(
                        status_code=500,
                        content={
                            "error": result.get('explanation'),
                            "processing_time": time.time() - start_time
                        }
                    )
                fixed_code = result.get('fixed_code', '')
                explanation = result.get('explanation', '')
                return CodeResponse(
                    original_code=request.code,
                    processed_code=fixed_code,
                    explanation=explanation,
                    processing_time=time.time() - start_time
                )
            elif request.action == 'execute':
                if request.language.lower() == 'python':
                    execution_result = await execute_python_code(request.code, request.inputs)
                    result_dict = {
                        "stdout": execution_result.get("stdout", ""),
                        "stderr": execution_result.get("stderr", ""),
                        "exit_code": execution_result.get("exit_code", None),
                        "execution_time": execution_result.get("execution_time", None),
                        "libraries_detected": execution_result.get("libraries_detected", []),
                    }
                    if not result_dict["stdout"] and result_dict["stderr"]:
                        known_errors = ["ZeroDivisionError", "SyntaxError", "TypeError", "NameError", "IndexError", "KeyError"]
                        for err in known_errors:
                            if err in result_dict["stderr"]:
                                result_dict["stdout"] = result_dict["stderr"]
                                break
                        else:
                            result_dict["stdout"] = "[No output]"
                    if "visualizations" in execution_result:
                        result_dict["stdout"] += f"\n[Visualization files saved: {execution_result['visualizations']}]"
                    if "ml_output" in execution_result:
                        result_dict["stdout"] += f"\n[ML output: {execution_result['ml_output']}]"
                    return CodeResponse(
                        original_code=request.code,
                        execution_result=result_dict,
                        processing_time=time.time() - start_time
                    )
                else:
                    return JSONResponse(
                        status_code=400,
                        content={
                            "error": f"Execution is currently only supported for Python, not {request.language}",
                            "processing_time": time.time() - start_time
                        }
                    )
            return JSONResponse(
                status_code=400,
                content={
                    "error": f"Unsupported action: {request.action}",
                    "processing_time": time.time() - start_time
                }
            )
        except Exception as e:
            return JSONResponse(
                status_code=200,
                content={
                    "error": f"Error processing {request.action} action: {str(e)}",
                    "processing_time": time.time() - start_time
                }
            )
    except Exception as e:
        return JSONResponse(
            status_code=200,
            content={
                "error": f"An error occurred: {str(e)}",
                "processing_time": time.time() - start_time
            }
        )

# process_code_stream
async def process_code_stream(request: CodeRequest):
    start_time = time.time()
    try:
        if not CodeRequest.validate_code(request.code):
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Invalid code: Code cannot be empty",
                    "processing_time": time.time() - start_time
                }
            )
        if not CodeRequest.validate_language(request.language):
            return JSONResponse(
                status_code=400,
                content={
                    "error": f"Unsupported language: {request.language}",
                    "processing_time": time.time() - start_time
                }
            )
        if not CodeRequest.validate_action(request.action):
            return JSONResponse(
                status_code=400,
                content={
                    "error": f"Unsupported action: {request.action}",
                    "processing_time": time.time() - start_time
                }
            )
        if request.action not in ["analyze", "optimize", "fix", "hint"]:
            return JSONResponse(
                status_code=400,
                content={
                    "error": f"Streaming is not supported for action: {request.action}",
                    "processing_time": time.time() - start_time
                }
            )
        # ollama_available check should be handled at a higher level or injected
        prompt = build_prompt(request.action, request.code, request.language)
        model = "codellama" if request.action in ["analyze", "fix", "optimize"] else "llama3"
        max_tokens = estimate_max_tokens(prompt)
        async def event_generator():
            try:
                yield json.dumps({"type": "start", "action": request.action}) + "\n"
                # This should call the streaming LLM generator (to be injected)
                # For now, yield a stub
                yield json.dumps({"type": "chunk", "content": "[Streaming not implemented in modular version]"}) + "\n"
                yield json.dumps({"type": "end"}) + "\n"
            except Exception as e:
                yield json.dumps({"type": "error", "error": str(e)}) + "\n"
        return StreamingResponse(event_generator(), media_type="text/event-stream")
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Error setting up streaming: {str(e)}",
                "processing_time": time.time() - start_time
            }
        )

# process_code_batch
async def process_code_batch(request: BatchCodeRequest):
    start_time = time.time()
    try:
        valid, errors = BatchCodeRequest.validate_request(request)
        if not valid:
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Invalid batch request: " + ", ".join(errors),
                    "processing_time": time.time() - start_time
                }
            )
        # ollama_available check should be handled at a higher level or injected
        results = []
        for code in request.codes:
            try:
                single_request = CodeRequest(
                    code=code,
                    language=request.language,
                    action=request.action
                )
                single_response = await process_code(single_request)
                if isinstance(single_response, JSONResponse):
                    results.append(single_response.body)
                else:
                    results.append(single_response.dict())
            except Exception as e:
                results.append({
                    "error": f"Error processing this item: {str(e)}",
                    "code": code,
                    "processing_time": time.time() - start_time
                })
        return JSONResponse(
            content={
                "results": results,
                "count": len(results),
                "processing_time": time.time() - start_time
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": f"An error occurred while processing batch request: {str(e)}",
                "processing_time": time.time() - start_time
            }
        )

# fix_code_with_context
async def fix_code_with_context(request: ContextAwareFixRequest):
    # This should call the context-aware fix logic (to be modularized further)
    # For now, return a stub
    return JSONResponse(content={"message": "Context-aware fix not yet modularized."}) 