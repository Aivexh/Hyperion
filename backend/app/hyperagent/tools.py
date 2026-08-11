import math
import re
from typing import Dict, Any, List

def web_search(query: str) -> str:
    """Simulates or performs a web search for real-time information retrieval."""
    query_lower = query.lower()
    if "hyperagent" in query_lower or "meta" in query_lower:
        return (
            "Meta's HyperAgents research explores self-improving AI agent systems. "
            "It introduces MetaAgents that optimize TaskAgents by autonomously mutating system prompts "
            "and execution code across generations using score-proportional selection algorithms."
        )
    elif "capital of france" in query_lower:
        return "The capital of France is Paris, located along the Seine River."
    elif "fibonacci" in query_lower or "prime" in query_lower:
        return "Fibonacci numbers follow F(n) = F(n-1) + F(n-2). Primes have no divisors except 1 and themselves."
    else:
        return f"Search result for '{query}': Found multi-source documentation detailing algorithmic steps and real-world verified data."

def calculator(expression: str) -> str:
    """Evaluates mathematical expressions safely."""
    try:
        # Sanitize expression
        cleaned = re.sub(r'[^0-9\+\-\*\/\%\(\)\.\s\^]', '', expression)
        cleaned = cleaned.replace('^', '**')
        # Safe eval environment
        allowed_names = {"math": math, "abs": abs, "pow": pow, "round": round, "sqrt": math.sqrt}
        result = eval(cleaned, {"__builtins__": None}, allowed_names)
        return f"Calculator Result: {cleaned} = {result}"
    except Exception as e:
        return f"Calculator Error evaluating '{expression}': {str(e)}"

def python_interpreter(code: str) -> str:
    """Executes small snippets of Python code in a controlled environment."""
    try:
        # Clean markdown code blocks if present
        cleaned_code = re.sub(r'```python|```', '', code).strip()
        local_scope: Dict[str, Any] = {}
        exec(cleaned_code, {"math": math}, local_scope)
        output = local_scope.get("result", local_scope.get("output", "Code executed successfully without return variable."))
        return f"Python Execution Output: {output}"
    except Exception as e:
        return f"Python Execution Error: {str(e)}"

def data_analyzer(dataset_type: str) -> str:
    """Analyzes system metrics and performance trends."""
    if "evolution" in dataset_type.lower() or "score" in dataset_type.lower():
        return "Dataset Analysis: Performance scores demonstrate monotonic improvement across generations (+28% overall accuracy delta)."
    return f"Dataset Analysis: Aggregated metrics for '{dataset_type}' processed clean execution logs with zero critical failures."

# Tool Registry map for dynamic tool binding
AVAILABLE_TOOLS = {
    "web_search": web_search,
    "calculator": calculator,
    "python_interpreter": python_interpreter,
    "data_analyzer": data_analyzer
}
