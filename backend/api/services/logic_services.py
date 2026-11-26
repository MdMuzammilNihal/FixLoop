# Core logic functions for code analysis, optimization, fixing, hint generation, and execution

# Import all required modules and dependencies
import re
import math
import time
import sys
import asyncio
import tempfile
import subprocess
import traceback
from typing import List, Optional
import json
import httpx
import os
from datetime import datetime
import logging
import ast
from backend.api.services.cache_services import cache_manager

async def check_ollama_available():
    """Check if Ollama service is available by pinging the /api/tags endpoint."""
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            return response.status_code == 200
    except Exception:
        return False

def estimate_max_tokens(prompt: str) -> int:
    prompt_length = len(prompt)
    code_lines = prompt.count('\n')
    chars_per_token = 4.5
    estimated_tokens = int(prompt_length / chars_per_token)
    if prompt_length > 15000:
        base_tokens = 4096
    elif prompt_length > 10000:
        base_tokens = 3840
    elif prompt_length > 7000:
        base_tokens = 3584
    elif prompt_length > 4000:
        base_tokens = 3072
    elif prompt_length > 2000:
        base_tokens = 2560
    elif prompt_length > 1000:
        base_tokens = 2048
    else:
        base_tokens = 1536
    if code_lines > 300:
        complexity_adjustment = 1024
    elif code_lines > 200:
        complexity_adjustment = 768
    elif code_lines > 100:
        complexity_adjustment = 512
    elif code_lines > 50:
        complexity_adjustment = 384
    elif code_lines > 25:
        complexity_adjustment = 256
    else:
        complexity_adjustment = 128
    token_adjustment = 0
    import_count = prompt.count("import ") + prompt.count("from ") + prompt.count("#include") + prompt.count("using ")
    if import_count > 10:
        token_adjustment += 384
    elif import_count > 5:
        token_adjustment += 256
    elif import_count > 0:
        token_adjustment += 128
    function_patterns = ["def ", "function", "func ", "fn ", "void ", "int ", "String ", "public ", "private "]
    class_patterns = ["class ", "struct ", "interface ", "trait ", "enum "]
    function_count = sum(prompt.count(pattern) for pattern in function_patterns)
    class_count = sum(prompt.count(pattern) for pattern in class_patterns)
    if function_count > 10 or class_count > 5:
        token_adjustment += 512
    elif function_count > 5 or class_count > 3:
        token_adjustment += 384
    elif function_count > 2 or class_count > 1:
        token_adjustment += 256
    elif function_count > 0 or class_count > 0:
        token_adjustment += 128
    error_patterns = ["try:", "catch", "try {", "except", "throw", "throws", "raise ", "finally", "rescue"]
    if any(pattern in prompt for pattern in error_patterns):
        token_adjustment += 192
    async_patterns = ["async ", "await ", "Promise", "future", "coroutine", "yield", "then(", "completable"]
    if any(pattern in prompt for pattern in async_patterns):
        token_adjustment += 256
    regex_patterns = [r"r[\"'].*?[\"']", r"Regex", r"Pattern", r"/.*?/", r"regexp", r"RegExp"]
    if "regex" in prompt.lower() or any(re.search(pattern, prompt) for pattern in regex_patterns):
        token_adjustment += 192
    data_structure_patterns = [
        "HashMap", "Dictionary", "Map", "List", "ArrayList", "LinkedList", 
        "Tree", "Graph", "Stack", "Queue", "Heap", "Set", "dict(", "list("
    ]
    if any(pattern in prompt for pattern in data_structure_patterns):
        token_adjustment += 128
    repetition_score = detect_repetitive_patterns(prompt)
    token_adjustment -= repetition_score * 128
    if prompt_length > 10000 and (base_tokens + complexity_adjustment + token_adjustment) > 4000:
        return min(4000, int(base_tokens * 0.8) + min(500, complexity_adjustment + token_adjustment))
    return min(base_tokens + complexity_adjustment + token_adjustment, 4096)

def detect_repetitive_patterns(text):
    if not text or len(text) < 100:
        return 0
    lines = text.split('\n')
    if len(lines) < 10:
        return 0
    repetition_score = 0
    line_hashes = {}
    for line in lines:
        stripped = line.strip()
        if len(stripped) > 3:
            line_hash = hash(stripped)
            line_hashes[line_hash] = line_hashes.get(line_hash, 0) + 1
    repeated_lines = sum(1 for count in line_hashes.values() if count > 1)
    if len(lines) > 0:
        repetition_ratio = repeated_lines / len(lines)
        if repetition_ratio > 0.5:
            repetition_score = 3
        elif repetition_ratio > 0.3:
            repetition_score = 2
        elif repetition_ratio > 0.1:
            repetition_score = 1
    return repetition_score

def adaptive_timeout(prompt, base_timeout, task):
    prompt_length = len(prompt)
    if prompt_length > 10000:
        timeout_multiplier = 2.5
    elif prompt_length > 5000:
        timeout_multiplier = 2.0
    elif prompt_length > 2000:
        timeout_multiplier = 1.5
    else:
        timeout_multiplier = 1.0
    if task == "fix" or task == "optimize":
        task_multiplier = 1.5
    elif task == "analyze":
        task_multiplier = 1.2
    else:
        task_multiplier = 1.0
    adjusted_timeout = base_timeout * timeout_multiplier * task_multiplier
    min_timeout = 30.0
    max_timeout = 300.0
    return max(min_timeout, min(adjusted_timeout, max_timeout))

def extract_items(content_lines):
    if not content_lines:
        return []
    items = []
    current_item = []
    for line in content_lines:
        if (line.startswith('-') or (line and line[0].isdigit() and line[1:].startswith('.')) or 
            (line and line.strip().startswith('*'))):
            if current_item:
                items.append(' '.join(current_item))
                current_item = []
            current_item.append(line)
        else:
            current_item.append(line)
    if current_item:
        items.append(' '.join(current_item))
    if not items and content_lines:
        items = [' '.join(content_lines)]
    return items

def extract_line_info_from_error(error_message, code):
    line_info = {"line": 1, "column": 1}
    patterns = [
        r"line (\d+)",
        r"line (\d+), column (\d+)",
        r"at line (\d+)",
        r"in line (\d+)"
    ]
    for pattern in patterns:
        match = re.search(pattern, error_message, re.IGNORECASE)
        if match:
            line_info["line"] = int(match.group(1))
            if len(match.groups()) > 1:
                line_info["column"] = int(match.group(2))
            break
    return line_info

def simplify_prompt(prompt, language):
    if len(prompt) > 5000:
        code_pattern = f"```{language}(.*?)```"
        code_matches = re.findall(code_pattern, prompt, re.DOTALL)
        if code_matches:
            code_block = max(code_matches, key=len)
            return f"Fix the following {language} code:\n```{language}\n{code_block.strip()}\n```"
        else:
            return f"Process the following text:\n{prompt[:4000]}..."
    else:
        return prompt

def build_prompt(action, code, language):
    if action == "analyze":
        return (
            f"You are a world-class {language} code reviewer. Analyze the following code.\n"
            "Return a JSON object with 'errors', 'warnings', and 'suggestions'. Be concise. Limit each list to 3 items.\n"
            f"Code:\n{code}\n"
            "Output format:\n{'errors':[],'warnings':[],'suggestions':[]}"
        )
    elif action == "optimize":
        return (
            f"You are a senior {language} performance engineer. Optimize the following code for speed and readability.\n"
            "First, explain your optimizations in 1-2 sentences, then output the optimized code.\n"
            f"Code:\n{code}\n"
            "Output format:\nExplanation: ...\nOptimized Code:\n<code>"
        )
    elif action == "hint":
        return (
            f"You are a {language} coding teacher. Give exactly 3 helpful hints to improve this code, but do not provide the full solution. Be brief.\n"
            f"Code:\n{code}\n"
            "Output format:\n1. ...\n2. ...\n3. ..."
        )
    elif action == "fix":
        return (
            f"You are an expert {language} programmer. Fix all bugs and issues in this code.\n"
            "First, identify the bugs/issues in 1-2 sentences, then provide the complete fixed code.\n"
            f"Code:\n{code}\n"
            "Output format:\nExplanation: ...\nFixed Code:\n<code>"
        )
    elif action == "execute":
        return (
            f"You are a {language} code execution assistant. Explain what this code does and predict its output.\n"
            f"Code:\n{code}\n"
            "Output format:\nExplanation: ...\nPredicted Output: ..."
        )
    else:
        return code

# --- Ollama LLM Generation Helper ---
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
# Low temperature: code fixing needs precision, and it makes answers repeatable (and cacheable).
OLLAMA_TEMPERATURE = float(os.getenv("FIXLOOP_TEMPERATURE", "0.2"))
logger = logging.getLogger(__name__)

async def ollama_generate(prompt: str, model: str = OLLAMA_MODEL, max_tokens: int = 2048, timeout: float = 90.0, task: str = None, language: str = None, temperature: float = None):
    """Generate text with Ollama in non-streaming mode. Successful responses are cached."""
    temperature = OLLAMA_TEMPERATURE if temperature is None else temperature
    cache_key = cache_manager.make_key(OLLAMA_BASE_URL, model, max_tokens, temperature, prompt)
    cached = cache_manager.get(cache_key)
    if cached is not None:
        return cached
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": temperature
                    }
                }
            )
            if response.status_code != 200:
                return f"Error from Ollama API: {response.status_code}"
            data = response.json()
            text = data.get("response", "")
            if text.strip():
                cache_manager.set(cache_key, text)
            return text
    except Exception as e:
        return f"Error during Ollama generation: {str(e)}"


async def ollama_stream(prompt: str, model: str = OLLAMA_MODEL, max_tokens: int = 2048, timeout: float = 120.0):
    """Yield text chunks from Ollama as they are generated."""
    async with httpx.AsyncClient(timeout=timeout) as client:
        async with client.stream(
            "POST",
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": True,
                "options": {"num_predict": max_tokens, "temperature": OLLAMA_TEMPERATURE},
            },
        ) as response:
            if response.status_code != 200:
                raise RuntimeError(f"Ollama API returned {response.status_code}")
            async for line in response.aiter_lines():
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if data.get("response"):
                    yield data["response"]
                if data.get("done"):
                    break


# --- Main Logic Functions (Full Implementations) ---

def _file_issue(issue, details, section, errors, warnings, suggestions):
    """Put a parsed issue into the right bucket: the section header it appeared under wins,
    and the keywords in its text are only a fallback when no header was seen."""
    text = f"{issue}\n" + "\n".join(details)
    if section == "errors":
        errors.append(text)
    elif section == "warnings":
        warnings.append(text)
    elif section == "suggestions":
        suggestions.append(text)
    elif "error" in issue.lower():
        errors.append(text)
    elif "warning" in issue.lower():
        warnings.append(text)
    else:
        suggestions.append(text)


async def analyze_code(code: str, language: str):
    """Analyze code for errors, warnings, and suggestions with category-based organization. Always returns a structured response with all keys."""
    prompt = f"""You are a professional code analyzer with expertise in {language}. Analyze this code carefully for bugs, inefficiencies, and style issues. Be thorough and comprehensive.\n\nCode to analyze:\n```{language}\n{code}\n```\n\nLook for these specific categories of issues and provide detailed analysis for each:\n1. SYNTAX ERRORS: Code that will not compile or run due to language syntax violations\n2. LOGIC BUGS: Incorrect program logic, off-by-one errors, incorrect conditions, edge cases\n3. SECURITY VULNERABILITIES: Injection risks, unsafe operations, authentication issues\n4. PERFORMANCE INEFFICIENCIES: Time/space complexity issues, redundant operations, excessive memory usage\n5. STYLE VIOLATIONS: Naming conventions, indentation, code organization, readability issues\n6. DESIGN ISSUES: Poor architecture, tight coupling, violating design principles\n7. INPUT VALIDATION: Missing or improper validation of user inputs or data\n8. ERROR HANDLING: Missing or improper error handling, silent failures\n9. POTENTIAL EDGE CASES: Boundary conditions that may cause issues\n\nFormat your analysis with the following structure:\n1. First provide a brief summary of the code and its purpose (1-2 sentences)\n2. Then list issues in these categories:\n   - ERRORS: Critical bugs that will cause the code to fail (syntax errors, runtime crashes)\n   - WARNINGS: Issues that don't break the code but could cause problems (logic bugs, performance issues)\n   - SUGGESTIONS: Ways to improve the code quality, readability, or performance\n\nFor each issue identified, use this format:\n- CATEGORY - [LINE X]: Brief description of the issue\n  * IMPACT: How serious is this issue and what problems might it cause\n  * FIX: A specific, actionable recommendation to fix the issue\n  * EXAMPLE: Brief code example showing how to fix the issue (when applicable)\n\nUse specific line numbers whenever possible to help locate issues.\n"""
    max_tokens = estimate_max_tokens(prompt)
    result = await ollama_generate(prompt, OLLAMA_MODEL, max_tokens, timeout=60.0, task="analyze", language=language)
    logger.info(f"[DEBUG] LLM analyze_code output: {result}")
    try:
        if not isinstance(result, str) or result.startswith("Error") or result.startswith("Ollama is not available"):
            return {
                "code_summary": "",
                "errors": [result],
                "warnings": [],
                "suggestions": [],
                "raw": result
            }
        errors = []
        warnings = []
        suggestions = []
        code_summary = ""
        sections = {"errors": [], "warnings": [], "suggestions": []}
        lines = result.split('\n')
        current_section = None
        section_buffer = []
        current_issue = None
        issue_section = None
        current_details = []
        summary_found = False
        for i, line in enumerate(lines):
            if not summary_found and len(line.strip()) > 10 and not line.lower().startswith(('error', 'warning', 'suggest', '- ', '* ', '#')):
                code_summary = line.strip()
                summary_found = True
                if i + 1 < len(lines) and not any(marker in lines[i+1].lower() for marker in ('error', 'warning', 'suggest', 'category')):
                    code_summary += " " + lines[i+1].strip()
                break
        for line in lines:
            line = line.strip()
            if not line:
                continue
            lower_line = line.lower()
            is_header = any(h in lower_line for h in (
                "errors:", "error section:", "warnings:", "warning section:",
                "suggestions:", "suggestion section:"))
            if is_header and current_issue:
                # a new section starts: the issue being collected belongs to the previous one
                _file_issue(current_issue, current_details, issue_section, errors, warnings, suggestions)
                current_issue = None
                current_details = []
            if "errors:" in lower_line or "error section:" in lower_line:
                if current_section and section_buffer:
                    sections[current_section].extend(section_buffer)
                current_section = "errors"
                section_buffer = []
                continue
            elif "warnings:" in lower_line or "warning section:" in lower_line:
                if current_section and section_buffer:
                    sections[current_section].extend(section_buffer)
                current_section = "warnings"
                section_buffer = []
                continue
            elif "suggestions:" in lower_line or "suggestion section:" in lower_line:
                if current_section and section_buffer:
                    sections[current_section].extend(section_buffer)
                current_section = "suggestions"
                section_buffer = []
                continue
            line_number_match = re.search(r'\[LINE\s+(\d+)\]', line, re.IGNORECASE)
            category_match = re.search(r'^(.*?)\s*-\s*\[LINE', line, re.IGNORECASE)
            if line_number_match and category_match:
                if current_issue:
                    _file_issue(current_issue, current_details, issue_section, errors, warnings, suggestions)
                current_issue = line
                issue_section = current_section
                current_details = []
                continue
            if line.startswith(('* IMPACT:', '* FIX:', '* EXAMPLE:', '*IMPACT:', '*FIX:', '*EXAMPLE:')):
                if current_issue:
                    current_details.append(line)
                    continue
            if current_issue:
                current_details.append(line)
            elif current_section:
                section_buffer.append(line)
        if current_issue:
            _file_issue(current_issue, current_details, issue_section, errors, warnings, suggestions)
        if current_section and section_buffer:
            sections[current_section].extend(section_buffer)
        for section_name, section_content in sections.items():
            extracted_items = extract_items(section_content)
            if section_name == "errors":
                errors.extend(extracted_items)
            elif section_name == "warnings":
                warnings.extend(extracted_items)
            elif section_name == "suggestions":
                suggestions.extend(extracted_items)
        if not any([errors, warnings, suggestions]):
            for line in lines:
                line = line.strip()
                if line.startswith('-') or (line and line[0].isdigit() and line[1:].startswith('.')):
                    lower_line = line.lower()
                    if "error" in lower_line:
                        errors.append(line)
                    elif "warning" in lower_line:
                        warnings.append(line)
                    else:
                        suggestions.append(line)
        if not any([errors, warnings, suggestions]):
            for line in lines:
                line = line.strip()
                if not line or len(line) < 10:
                    continue
                lower_line = line.lower()
                if "error" in lower_line or "bug" in lower_line or "crash" in lower_line:
                    errors.append(line)
                elif "warning" in lower_line or "issue" in lower_line or "concern" in lower_line:
                    warnings.append(line)
                elif "suggest" in lower_line or "improve" in lower_line or "better" in lower_line:
                    suggestions.append(line)
        if not any([errors, warnings, suggestions]) and result.strip():
            suggestions = [result.strip()]
        return {
            "code_summary": code_summary,
            "errors": errors if isinstance(errors, list) else [],
            "warnings": warnings if isinstance(warnings, list) else [],
            "suggestions": suggestions if isinstance(suggestions, list) else [],
            "raw": result.strip()
        }
    except Exception as e:
        logger.error(f"Error parsing analysis result: {str(e)}")
        return {
            "code_summary": "",
            "errors": [f"Error parsing the analysis result: {str(e)}"],
            "warnings": [],
            "suggestions": [],
            "raw": str(result)
        }

async def optimize_code(code: str, language: str):
    """Optimize code for performance and readability with detailed metrics."""
    prompt = f"""You are a senior {language} performance engineer. Optimize the following code for performance, readability, and best practices.\n\n```{language}\n{code}\n```\n\nIMPORTANT FORMATTING INSTRUCTIONS:\n1. Start with "Optimization Summary:" followed by a brief overview of the key optimizations (2-3 sentences)\n2. Then provide "Performance Impact:" with specific metrics (e.g., O(n²) → O(n log n), memory usage improvements)\n3. Next, list "Key Optimizations:" with bullet points for the main improvements\n4. Finally, provide the complete optimized code inside a code block\n5. Start the optimized code section with "Optimized Code:" on its own line\n6. Format the optimized code in a code block starting with ```{language} and ending with ```\n7. Do not omit any parts of the code - provide the complete optimized version\n\nExample format:\nOptimization Summary: (Brief overview of optimizations)\n\nPerformance Impact: (Time & space complexity changes, memory usage improvements)\n\nKey Optimizations:\n- (First optimization)\n- (Second optimization)\n- (Third optimization)\n\nOptimized Code:\n```{language}\n(Complete optimized code here)\n```\n"""
    max_tokens = estimate_max_tokens(prompt) + 1024
    result = await ollama_generate(
        prompt, 
        OLLAMA_MODEL, 
        max_tokens, 
        timeout=180.0,  # Longer timeout for optimization
        task="optimize", 
        language=language
    )
    logger.info(f"[DEBUG] LLM optimize_code output: {result}")
    if not isinstance(result, str) or result.startswith("Error") or result.startswith("Ollama is not available"):
        return {"explanation": result, "optimized_code": code, "performance_metrics": {"error": result}}
    try:
        explanation = ""
        optimized_code = ""
        performance_metrics = {}
        key_optimizations = []
        if "Optimization Summary:" in result:
            parts = result.split("Optimization Summary:")
            summary = parts[1].split("\n\n", 1)[0].strip()
            performance_metrics["summary"] = summary
        if "Performance Impact:" in result:
            parts = result.split("Performance Impact:")
            impact = parts[1].split("\n\n", 1)[0].strip()
            performance_metrics["impact"] = impact
            time_complexity_patterns = [
                r"O\(([^)]+)\)\s*(?:→|->)\s*O\(([^)]+)\)",
                r"from\s+O\(([^)]+)\)\s+to\s+O\(([^)]+)\)",
                r"time\s+complexity\s+(?:improved|reduced)\s+from\s+O\(([^)]+)\)\s+to\s+O\(([^)]+)\)"
            ]
            complexity_matches = []
            for pattern in time_complexity_patterns:
                matches = re.findall(pattern, impact, re.IGNORECASE)
                if matches:
                    complexity_matches.extend(matches)
                    break
            if complexity_matches:
                performance_metrics["time_complexity"] = {
                    "before": f"O({complexity_matches[0][0]})",
                    "after": f"O({complexity_matches[0][1]})"
                }
                before = complexity_matches[0][0].lower().strip()
                after = complexity_matches[0][1].lower().strip()
                def normalize_complexity(expr):
                    expr = expr.lower().replace(" ", "")
                    expr = expr.replace("logn", "log(n)").replace("nlogn", "n*log(n)")
                    expr = expr.replace("n²", "n^2").replace("n³", "n^3")
                    return expr
                norm_before = normalize_complexity(before)
                norm_after = normalize_complexity(after)
                improvement_descriptions = {
                    ("n^3", "n^2"): "Cubic to quadratic - significant improvement for large inputs",
                    ("n^2", "n*log(n)"): "Quadratic to linearithmic - major improvement for medium to large inputs",
                    ("n^2", "n"): "Quadratic to linear - dramatic improvement for all input sizes",
                    ("n*log(n)", "n"): "Linearithmic to linear - noticeable improvement for large inputs",
                    ("n", "log(n)"): "Linear to logarithmic - enormous improvement for large inputs",
                    ("2^n", "n^2"): "Exponential to polynomial - transformative improvement",
                    ("2^n", "n*log(n)"): "Exponential to linearithmic - transformative improvement",
                    ("2^n", "n"): "Exponential to linear - transformative improvement"
                }
                for (from_complexity, to_complexity), description in improvement_descriptions.items():
                    if from_complexity in norm_before and to_complexity in norm_after:
                        performance_metrics["improvement_analysis"] = description
                        break
                try:
                    complexity_map = {
                        "1": lambda n: 1,
                        "log(n)": lambda n: math.log2(n),
                        "n": lambda n: n,
                        "n*log(n)": lambda n: n * math.log2(n),
                        "n^2": lambda n: n**2,
                        "n^3": lambda n: n**3,
                        "2^n": lambda n: 2**n
                    }
                    before_func = None
                    after_func = None
                    for complexity_term, func in complexity_map.items():
                        if complexity_term in norm_before:
                            before_func = func
                        if complexity_term in norm_after:
                            after_func = func
                    if before_func and after_func:
                        sample_sizes = [10, 100, 1000, 10000]
                        speedups = {}
                        for size in sample_sizes:
                            try:
                                before_time = before_func(size)
                                after_time = after_func(size)
                                if after_time > 0:
                                    speedup = before_time / after_time
                                    if speedup > 1e6:
                                        speedups[str(size)] = "over 1,000,000x"
                                    else:
                                        speedups[str(size)] = f"{speedup:.1f}x"
                            except (OverflowError, ValueError):
                                speedups[str(size)] = "N/A (overflow)"
                        if speedups:
                            performance_metrics["theoretical_speedups"] = speedups
                except Exception as e:
                    pass
            memory_patterns = [
                r"memory\s+usage\s+(?:improved|reduced)\s+by\s+(?:approximately\s+)?(\d+[%xX])",
                r"reduces\s+memory\s+(?:usage|consumption)\s+by\s+(?:approximately\s+)?(\d+[%xX])",
                r"memory\s+(?:usage|consumption|footprint)\s+(?:is|reduced)\s+(?:by)?\s+(\d+[%xX])"
            ]
            for pattern in memory_patterns:
                memory_matches = re.findall(pattern, impact, re.IGNORECASE)
                if memory_matches:
                    performance_metrics["memory_improvement"] = memory_matches[0]
                    break
            if "execution time" in impact.lower() or "runtime" in impact.lower():
                time_reduction_pattern = r"(?:execution time|runtime)(?:\s+is)?\s+(?:improved|reduced)\s+by\s+(?:approximately\s+)?(\d+[%xX])"
                time_matches = re.findall(time_reduction_pattern, impact, re.IGNORECASE)
                if time_matches:
                    performance_metrics["execution_time_improvement"] = time_matches[0]
        if "Key Optimizations:" in result:
            parts = result.split("Key Optimizations:")
            optimizations_text = parts[1].split("\n\n", 1)[0].strip()
            for line in optimizations_text.split("\n"):
                if line.strip().startswith("- "):
                    key_optimizations.append(line.strip()[2:])
                elif line.strip().startswith("* "):
                    key_optimizations.append(line.strip()[2:])
            categorized_optimizations = {
                "algorithm_changes": [],
                "data_structure_improvements": [],
                "code_efficiency": [],
                "readability_improvements": []
            }
            for opt in key_optimizations:
                lower_opt = opt.lower()
                if any(term in lower_opt for term in ["algorithm", "complexity", "approach", "method", "strategy"]):
                    categorized_optimizations["algorithm_changes"].append(opt)
                elif any(term in lower_opt for term in ["data structure", "hashmap", "dictionary", "array", "list", "set"]):
                    categorized_optimizations["data_structure_improvements"].append(opt)
                elif any(term in lower_opt for term in ["cache", "memoization", "redundant", "duplicate", "unnecessary", "computation"]):
                    categorized_optimizations["code_efficiency"].append(opt)
                elif any(term in lower_opt for term in ["readable", "readability", "naming", "documentation", "comment", "structure"]):
                    categorized_optimizations["readability_improvements"].append(opt)
                else:
                    categorized_optimizations["code_efficiency"].append(opt)
            performance_metrics["optimizations"] = {k: v for k, v in categorized_optimizations.items() if v}
            performance_metrics["key_optimizations"] = key_optimizations
        if "Optimized Code:" in result and "```" in result:
            parts = result.split("Optimized Code:")
            code_section = parts[1].strip()
            if f"```{language}" in code_section:
                code_block = code_section.split(f"```{language}", 1)[1].split("```", 1)[0].strip()
                optimized_code = code_block
            elif "```" in code_section:
                code_block = code_section.split("```", 1)[1].split("```", 1)[0].strip()
                optimized_code = code_block
            else:
                optimized_code = code_section
        if not optimized_code and "```" in result:
            code_blocks = result.split("```")
            longest_block = ""
            for i in range(1, len(code_blocks), 2):
                if i < len(code_blocks):
                    block = code_blocks[i]
                    for lang in ["python", "java", "cpp", "javascript", "typescript", "csharp", "go", "ruby", "rust", "php"]:
                        if block.startswith(lang):
                            block = block[len(lang):].strip()
                            break
                    if len(block) > len(longest_block):
                        longest_block = block
            optimized_code = longest_block.strip()
            explanation_parts = result.split("```", 1)
            if explanation_parts:
                explanation = explanation_parts[0].strip()
        else:
            if "Optimized Code:" in result:
                explanation = result.split("Optimized Code:", 1)[0].strip()
            else:
                explanation = result.strip()
        if not explanation:
            explanation = "Code has been optimized for better performance and readability."
        if language == "python":
            performance_metrics["language_specific_insights"] = [
                "Consider profiling with cProfile for a more detailed performance analysis",
                "Use Python's built-in functions and libraries (like NumPy for numerical operations) for optimal performance",
                "List comprehensions are generally faster than for loops for creating lists"
            ]
        elif language == "javascript":
            performance_metrics["language_specific_insights"] = [
                "Consider using Chrome DevTools Performance tab for detailed runtime analysis",
                "Modern JavaScript features like map/reduce/filter are often more optimized than manual loops",
                "Avoid frequent DOM manipulations which cause reflows and repaints"
            ]
        elif language == "java":
            performance_metrics["language_specific_insights"] = [
                "Use a profiler like VisualVM or JProfiler for detailed performance analysis",
                "Consider using StringBuilder for string concatenation in loops",
                "Favor efficient collections like HashSet over ArrayList when order is not important"
            ]
        if code and optimized_code:
            code_metrics = {}
            original_lines = len(code.strip().split('\n'))
            optimized_lines = len(optimized_code.strip().split('\n'))
            line_diff = optimized_lines - original_lines
            line_percent = ((optimized_lines / original_lines) - 1) * 100 if original_lines > 0 else 0
            code_metrics["line_count"] = {
                "original": original_lines,
                "optimized": optimized_lines,
                "difference": line_diff,
                "percent_change": f"{line_percent:.1f}%"
            }
            original_chars = len(code.strip())
            optimized_chars = len(optimized_code.strip())
            char_diff = optimized_chars - original_chars
            char_percent = ((optimized_chars / original_chars) - 1) * 100 if original_chars > 0 else 0
            code_metrics["character_count"] = {
                "original": original_chars,
                "optimized": optimized_chars,
                "difference": char_diff,
                "percent_change": f"{char_percent:.1f}%"
            }
            def estimate_cyclomatic_complexity(code_text):
                control_structures = [
                    "if ", "else:", "elif ", "for ", "while ", "try:", 
                    "except:", "with ", "case ", "switch", "?", ":"
                ]
                count = 0
                for structure in control_structures:
                    count += code_text.count(structure)
                return count
            original_complexity = estimate_cyclomatic_complexity(code)
            optimized_complexity = estimate_cyclomatic_complexity(optimized_code)
            complexity_diff = optimized_complexity - original_complexity
            complexity_percent = ((optimized_complexity / original_complexity) - 1) * 100 if original_complexity > 0 else 0
            code_metrics["complexity_estimate"] = {
                "original": original_complexity,
                "optimized": optimized_complexity,
                "difference": complexity_diff,
                "percent_change": f"{complexity_percent:.1f}%"
            }
            function_patterns = {
                "python": ["def ", "lambda"],
                "javascript": ["function", "=>", "function*"],
                "typescript": ["function", "=>", "function*"],
                "java": ["public ", "private ", "protected ", "void ", "class "],
                "cpp": ["void ", "int ", "double ", "float ", "class "],
                "csharp": ["void ", "public ", "private ", "protected ", "class "],
                "go": ["func "]
            }
            patterns = function_patterns.get(language.lower(), ["function", "def"])
            original_functions = sum(code.count(p) for p in patterns)
            optimized_functions = sum(optimized_code.count(p) for p in patterns)
            function_diff = optimized_functions - original_functions
            code_metrics["function_count"] = {
                "original": original_functions,
                "optimized": optimized_functions,
                "difference": function_diff
            }
            performance_metrics["code_metrics"] = code_metrics
        if not performance_metrics:
            performance_metrics = {
                "summary": "Code has been optimized for better performance and readability.",
                "key_optimizations": extract_items(explanation.split("\n"))
            }
        if not optimized_code:
            logger.warning("Failed to extract optimized code from the result")
            optimized_code = code
            explanation += "\n\nNote: Failed to extract optimized code. Please try again with a simpler query."
        logger.info(f"Successfully extracted optimized code ({len(optimized_code)} chars) and performance metrics")
        return {
            "explanation": explanation,
            "optimized_code": optimized_code,
            "performance_metrics": performance_metrics
        }
    except Exception as e:
        logger.error(f"Error parsing optimization result: {str(e)}\nResult: {result}")
        return {
            "explanation": f"Error parsing the optimization result: {str(e)}",
            "optimized_code": code,
            "performance_metrics": {"error": str(e)}
        }

async def generate_hints(code: str, language: str):
    """Generate exactly 5 clear, actionable hints for improving code without giving the full solution."""
    prompt = f"""You are a coding teacher. Give exactly 5 clear, actionable, and non-overlapping hints to improve this {language} code without providing the complete solution. Each hint should be concise, specific, and helpful for a student to improve their code. Do not provide the full solution or repeat hints.\n\n```{language}\n{code}\n```\n\nFormat your response as a numbered list of exactly 5 hints, each on a new line. Do not provide the full solution. Do not repeat hints. Do not include explanations, just the hints themselves.\n"""
    max_tokens = estimate_max_tokens(prompt)
    result = await ollama_generate(prompt, OLLAMA_MODEL, max_tokens, timeout=45.0, task="hint", language=language)
    logger.info(f"[DEBUG] LLM generate_hints output: {result}")
    hints = []
    for line in result.split('\n'):
        line = line.strip()
        if line and (re.match(r'^[1-5]\. ', line) or re.match(r'^- ', line)):
            hints.append(line)
    if len(hints) < 5:
        hints = [l.strip() for l in result.split('\n') if l.strip()][:5]
    while len(hints) < 5:
        hints.append("[Add another hint here]")
    if len(hints) > 5:
        hints = hints[:5]
    return {
        "hints": hints
    }

def python_lint(code: str, limit: int = 8):
    """Static analysis with pyflakes: cheap, deterministic hints about real defects
    (undefined names, syntax errors, ...). Returns short strings like "line 4: undefined name 'ss'"."""
    try:
        from pyflakes import api as pyflakes_api, reporter as pyflakes_reporter
    except ImportError:
        return []
    import io
    out, err = io.StringIO(), io.StringIO()
    pyflakes_api.check(code, "snippet.py", pyflakes_reporter.Reporter(out, err))
    findings = []
    for raw in (out.getvalue() + err.getvalue()).splitlines():
        parts = raw.split(":", 3)
        if len(parts) < 4 or not parts[0].endswith("snippet.py"):
            continue  # continuation lines (source excerpts, carets)
        message = parts[3].strip()
        if "imported but unused" in message or "never used" in message:
            continue  # noise: does not explain a bug
        findings.append(f"line {parts[1]}: {message}")
    return findings[:limit]


async def fix_code(code: str, language: str, extra_context: str = ""):
    """Fix bugs in the code. Static-analysis findings (Python) and extra context are added to the prompt."""
    prompt = (
        f"You are an expert {language} programmer. The code below has a bug. Fix it.\n\n"
        f"```{language}\n{code}\n```\n\n"
        "Rules:\n"
        "- Make the smallest change that fixes the bug. Keep function names, signatures and all other behavior unchanged.\n"
        "- Do not add features, validation, type checks or comments that are not needed to fix the bug.\n"
        "- If the code crashes on some input (for example an empty list or a missing key), handle that case gracefully.\n"
        "- Work out what the code is supposed to do from its names and the example call, then check it against that intent. "
        "Typical logic bugs: off-by-one in ranges, loop bounds and comparisons; a wrong constant or operator; a missing or extra character in a literal; "
        "a missing case such as an empty input, a single element, or repeated separators.\n"
        "- If the code can raise an exception on bad input, catch it and return a sensible value instead of letting it propagate.\n"
        "- Return the complete fixed code, not a fragment.\n\n"
        "Answer in exactly this format:\n"
        "Explanation:\n<say what the code should do, trace it on one small example to find where it goes wrong, then name the bug; two to four sentences>\n\n"
        f"Fixed Code:\n```{language}\n<complete fixed code>\n```\n"
    )
    findings = python_lint(code) if language.lower() == "python" else []
    if findings:
        prompt += "\nStatic analysis of the original code reported:\n" + "\n".join(f"- {f}" for f in findings) + "\n"
    if extra_context:
        prompt += "\n\nAdditional context to take into account:\n" + extra_context + "\n"
    max_tokens = estimate_max_tokens(prompt) + 1024
    start_time = time.time()
    result = await ollama_generate(prompt, OLLAMA_MODEL, max_tokens, timeout=120.0, task="fix", language=language)
    logger.info(f"[DEBUG] LLM fix_code output: {result}")
    try:
        explanation = ""
        fixed_code = ""
        bugs_found = []
        bug_fixes = []
        if "Explanation:" in result and "Fixed Code:" in result:
            parts = result.split("Fixed Code:")
            explanation = parts[0].replace("Explanation:", "").strip()
            code_part = parts[1].strip()
            if f"```{language}" in code_part:
                code_block = code_part.split(f"```{language}", 1)[1].split("```", 1)[0].strip()
                fixed_code = code_block
            elif "```" in code_part:
                code_block = code_part.split("```", 1)[1].split("```", 1)[0].strip()
                fixed_code = code_block
            else:
                fixed_code = code_part
            if "Bugs Found:" in explanation:
                bugs_section = explanation.split("Bugs Found:", 1)[1].strip()
                bug_lines = bugs_section.split("\n")
                current_bug = None
                for line in bug_lines:
                    line = line.strip()
                    if line.startswith("- BUG:"):
                        current_bug = line[7:].strip()
                        bugs_found.append(current_bug)
                    elif line.startswith("- FIX:") and bugs_found:
                        bug_fixes.append(line[6:].strip())
        elif f"```{language}" in result:
            parts = result.split(f"```{language}")
            explanation = parts[0].strip()
            if len(parts) > 2:
                code_part = parts[-1].split("```", 1)[0].strip()
            else:
                code_part = parts[1].split("```", 1)[0].strip()
            fixed_code = code_part
        elif "```" in result:
            parts = result.split("```")
            explanation = parts[0].strip()
            largest_block = ""
            for i in range(1, len(parts), 2):
                if i < len(parts):
                    block = parts[i]
                    for lang in ["python", "java", "cpp", "javascript", "typescript", "csharp", "go", "ruby", "rust", "php"]:
                        if block.startswith(lang):
                            block = block[len(lang):].strip()
                            break
                    if len(block) > len(largest_block):
                        largest_block = block
            if largest_block:
                fixed_code = largest_block.strip()
            else:
                fixed_code = parts[1].strip() if len(parts) > 1 else ""
        fixed_code = re.sub(r"```\w*|```", "", fixed_code).strip()
        if not fixed_code:
            fixed_code = code
            explanation = "Could not generate a fix for the provided code."
        diff_summary = {}  # You can implement generate_diff_summary if needed
        response_data = {
            "original_code": code,
            "fixed_code": fixed_code,
            "explanation": explanation,
            "bugs_found": bugs_found,
            "bug_fixes": bug_fixes,
            "diff_summary": diff_summary,
            "processing_time": time.time() - start_time
        }
        return response_data
    except Exception as e:
        logger.error(f"Error parsing fix result: {str(e)}\nResult: {result}")
        return {
            "explanation": f"Error parsing the result: {str(e)}",
            "fixed_code": code,
            "bugs_found": [],
            "bug_fixes": [],
            "diff_summary": {},
            "processing_time": time.time() - start_time
        }

def check_python_syntax(code: str):
    """Return None if the code parses, otherwise a short description of the SyntaxError."""
    try:
        ast.parse(code)
        return None
    except SyntaxError as e:
        return f"SyntaxError: {e.msg} (line {e.lineno})"


async def fix_code_self_correcting(code: str, language: str, max_attempts: int = 3,
                                   verify_execution: bool = False, extra_context: str = ""):
    """Fix code, then verify the result and ask the model to retry with the failure as feedback.

    Verification always includes a syntax check for Python. With verify_execution=True the fixed
    code is also run (WARNING: executes on the host) and a non-zero exit code counts as a failure.
    The result carries an ``attempts`` list describing every try.
    """
    attempts = []
    base_context = extra_context
    if verify_execution and language.lower() == "python":
        # Run the original code first so the model sees the real error instead of guessing.
        original_run = await execute_python_code(code)
        trace = (original_run.get("stderr") or "").strip()[-800:]
        if original_run.get("exit_code") not in (0, None) and trace:
            base_context = (base_context + "\n" if base_context else "") + (
                "Running the original code fails with this error:\n" + trace
            )
    feedback = base_context
    result = None
    for attempt in range(1, max_attempts + 1):
        result = await fix_code(code, language, extra_context=feedback)
        fixed = result.get("fixed_code", "")
        problem = None
        if language.lower() == "python" and fixed and fixed != code:
            problem = check_python_syntax(fixed)
            if problem is None and verify_execution:
                run = await execute_python_code(fixed)
                if run.get("exit_code") not in (0, None):
                    problem = (run.get("stderr") or "non-zero exit code").strip()[-800:]
        attempts.append({"attempt": attempt, "ok": problem is None, "problem": problem})
        if problem is None:
            break
        feedback = (base_context + "\n" if base_context else "") + (
            f"Your previous fix failed verification with this error:\n{problem}\n"
            f"Previous attempt:\n```{language}\n{fixed}\n```\nFix it properly this time."
        )
    result["attempts"] = attempts
    result["verified"] = bool(attempts and attempts[-1]["ok"])
    return result


async def execute_python_code(code: str, inputs: Optional[List[str]] = None):
    """Safely execute Python code and return the result (fully async, non-blocking). Improved input() patch, Python version check, and error/output handling."""
    try:
        if sys.version_info < (3, 6):
            return {
                "stderr": "Error: Python version is too old. f-strings require Python 3.6 or newer.",
                "stdout": "",
                "execution_time": 0,
                "exit_code": -1
            }
        if not code or not isinstance(code, str):
            return {
                "stderr": "Error: Invalid or empty code provided.",
                "stdout": "",
                "execution_time": 0,
                "exit_code": -1
            }
        if not code.strip():
            return {
                "stderr": "Error: No code provided for execution.",
                "stdout": "",
                "execution_time": 0,
                "exit_code": -1
            }
        if inputs is None:
            inputs = []
        elif not isinstance(inputs, list):
            return {
                "stderr": "Error: Inputs must be a list of strings.",
                "stdout": "",
                "execution_time": 0,
                "exit_code": -1
            }
        inputs = [str(i).strip() for i in inputs if i is not None and str(i).strip()]
        if 'input(' in code:
            input_patch = '''
import sys
_INPUTS = {inputs}
_input_index = 0
def input(prompt=''):
    global _input_index
    try:
        prompt_str = str(prompt)
    except Exception:
        prompt_str = ''
    print(prompt_str, end='')
    if _input_index < len(_INPUTS):
        value = _INPUTS[_input_index]
        _input_index += 1
        print(value)
        return value
    else:
        print("")
        return ""
'''.replace('{inputs}', repr(inputs))
            modified_code = input_patch + "\n# Original code starts here\n" + code
        else:
            modified_code = code
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as temp_file:
            temp_file_path = temp_file.name
            temp_file.write(modified_code.encode())
        start_time = time.time()
        try:
            if sys.platform == 'win32':
                try:
                    process = subprocess.Popen(
                        [sys.executable, temp_file_path],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    try:
                        stdout, stderr = process.communicate(timeout=10)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        os.unlink(temp_file_path)
                        return {
                            "stderr": "Execution timed out (limit: 10 seconds). This may indicate an infinite loop or inefficient code.",
                            "stdout": "",
                            "execution_time": 10.0,
                            "exit_code": -1
                        }
                except MemoryError:
                    os.unlink(temp_file_path)
                    return {
                        "stderr": "[FixLoop] MemoryError: The code attempted to use too much memory and was stopped.",
                        "stdout": "[FixLoop] MemoryError: The code attempted to use too much memory and was stopped.",
                        "execution_time": time.time() - start_time,
                        "exit_code": -2
                    }
            else:
                try:
                    process = await asyncio.create_subprocess_exec(
                        sys.executable, temp_file_path,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    try:
                        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=10)
                        stdout = stdout.decode()
                        stderr = stderr.decode()
                    except asyncio.TimeoutError:
                        process.kill()
                        await process.wait()
                        os.unlink(temp_file_path)
                        return {
                            "stderr": "Execution timed out (limit: 10 seconds). This may indicate an infinite loop or inefficient code.",
                            "stdout": "",
                            "execution_time": 10.0,
                            "exit_code": -1
                        }
                except MemoryError:
                    os.unlink(temp_file_path)
                    return {
                        "stderr": "[FixLoop] MemoryError: The code attempted to use too much memory and was stopped.",
                        "stdout": "[FixLoop] MemoryError: The code attempted to use too much memory and was stopped.",
                        "execution_time": time.time() - start_time,
                        "exit_code": -2
                    }
            execution_time = time.time() - start_time
            os.unlink(temp_file_path)
            # Always include full stderr in the response
            if not stdout.strip() and stderr.strip():
                stdout = stderr
            return {
                "stdout": stdout,
                "stderr": stderr,
                "execution_time": execution_time,
                "exit_code": process.returncode,
                "libraries_detected": []
            }
        except MemoryError:
            os.unlink(temp_file_path)
            return {
                "stderr": "[FixLoop] MemoryError: The code attempted to use too much memory and was stopped.",
                "stdout": "[FixLoop] MemoryError: The code attempted to use too much memory and was stopped.",
                "execution_time": time.time() - start_time,
                "exit_code": -2
            }
        except Exception as e:
            os.unlink(temp_file_path)
            return {
                "stderr": f"Error during execution: {str(e)}\n\nThis may be due to a system limitation or resource constraint.",
                "stdout": "",
                "execution_time": time.time() - start_time,
                "exit_code": -1
            }
    except Exception as e:
        return {
            "stderr": f"Error: {str(e)}\n\nPlease check your code for errors before execution.",
            "stdout": "",
            "execution_time": 0,
            "exit_code": -1
        } 