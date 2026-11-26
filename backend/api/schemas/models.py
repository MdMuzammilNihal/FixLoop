from typing import List, Optional, Dict, Any, Tuple
from pydantic import BaseModel

class CodeRequest(BaseModel):
    code: str
    language: str = "python"
    action: str = "analyze"  # analyze, optimize, hint, fix, execute
    inputs: Optional[List[str]] = None
    verify_execution: bool = False  # fix action: also run the fixed code to verify it (executes on the host)
    class Config:
        validate_assignment = True
    @classmethod
    def validate_code(cls, code: str) -> bool:
        return isinstance(code, str) and bool(code.strip())
    @classmethod
    def validate_language(cls, language: str) -> bool:
        supported_languages = [
            "python", "java", "cpp", "javascript", "typescript", 
            "csharp", "go", "ruby", "rust", "php"
        ]
        return language.lower() in supported_languages
    @classmethod
    def validate_action(cls, action: str) -> bool:
        valid_actions = ["analyze", "optimize", "hint", "fix", "execute"]
        return action.lower() in valid_actions
    @classmethod
    def validate_inputs(cls, inputs: Optional[List[str]]) -> bool:
        if inputs is None:
            return True
        return isinstance(inputs, list) and all(isinstance(i, str) for i in inputs)

class ChatRequest(BaseModel):
    message: str
    code: Optional[str] = None

class CodeResponse(BaseModel):
    original_code: str
    processed_code: Optional[str] = None
    explanation: Optional[str] = None
    hints: Optional[List[str]] = None
    errors: Optional[List[str]] = None
    warnings: Optional[List[str]] = None
    suggestions: Optional[List[str]] = None
    execution_result: Optional[dict] = None
    performance_metrics: Optional[Dict[str, Any]] = None
    attempts: Optional[List[Dict[str, Any]]] = None
    verified: Optional[bool] = None
    processing_time: float

class BatchCodeRequest(BaseModel):
    codes: List[str]
    language: str = "python"
    action: str = "analyze"
    class Config:
        validate_assignment = True
    @classmethod
    def validate_request(cls, request) -> tuple:
        if not isinstance(request.codes, list) or not request.codes:
            return False, "Request must include a non-empty 'codes' array."
        if not all(isinstance(code, str) and code.strip() for code in request.codes):
            return False, "All code entries must be non-empty strings."
        if not CodeRequest.validate_language(request.language):
            return False, f"Unsupported language: '{request.language}'."
        if not CodeRequest.validate_action(request.action):
            return False, f"Invalid action: '{request.action}'."
        supported_language_actions = {
            "python": ["analyze", "optimize", "hint", "fix", "execute"],
            "java": ["analyze", "optimize", "hint", "fix", "execute"],
            "cpp": ["analyze", "optimize", "hint", "fix", "execute"],
            "javascript": ["analyze", "optimize", "hint", "fix", "execute"],
            "typescript": ["analyze", "optimize", "hint", "fix"],
            "csharp": ["analyze", "optimize", "hint", "fix"],
            "go": ["analyze", "optimize", "hint", "fix"],
            "ruby": ["analyze", "optimize", "hint", "fix"],
            "rust": ["analyze", "optimize", "hint", "fix"],
            "php": ["analyze", "optimize", "hint", "fix"]
        }
        if request.action not in supported_language_actions.get(request.language, []):
            return False, f"Action '{request.action}' is not supported for language '{request.language}'."
        return True, ""

class IDERequest(BaseModel):
    code: str
    language: str = "python"
    action: str = "analyze"
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    inputs: Optional[List[str]] = None
    ide_type: str = "vscode"
    session_id: Optional[str] = None
    class Config:
        validate_assignment = True
    @classmethod
    def validate_request(cls, request) -> Tuple[bool, List[str]]:
        errors = []
        if not CodeRequest.validate_code(request.code):
            errors.append("Invalid code: Code cannot be empty")
        if not CodeRequest.validate_language(request.language):
            errors.append(f"Unsupported language: {request.language}")
        if not CodeRequest.validate_action(request.action):
            errors.append(f"Unsupported action: {request.action}")
        if request.inputs and not CodeRequest.validate_inputs(request.inputs):
            errors.append("Invalid inputs format")
        return len(errors) == 0, errors

class IDEResponse(BaseModel):
    original_code: str
    processed_code: Optional[str] = None
    explanation: Optional[str] = None
    hints: Optional[List[str]] = None
    errors: Optional[List[str]] = None
    execution_result: Optional[dict] = None
    performance_metrics: Optional[Dict[str, Any]] = None
    processing_time: float
    ide_specific: Optional[Dict[str, Any]] = None
    inline_diagnostics: Optional[List[Dict[str, Any]]] = None

class ContextAwareFixRequest(BaseModel):
    code: str
    language: str = "python"
    context: Optional[str] = None
    file_path: Optional[str] = None
    dependencies: Optional[List[str]] = None
    error_message: Optional[str] = None
    class Config:
        validate_assignment = True 