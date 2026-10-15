import ast
import logging
import math
import operator
import re

import httpx
import numpy as np

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# web_search
# ---------------------------------------------------------------------------

_SEARCH_URL = "https://api.duckduckgo.com/"
_SEARCH_TIMEOUT_SECONDS = 4.0
_FALLBACK_LABEL = "[Predefined fallback knowledge - NOT a live search result]"

# Predefined answers used ONLY when live search yields nothing. Patterns are
# deliberately specific so broad words such as "meta" or "france" on their own
# do not trigger them.
_FALLBACK_KNOWLEDGE = (
    (
        re.compile(r"\bhyper-?agents?\b"),
        "HyperAgents describes self-improving AI agent systems in which a "
        "meta-level agent modifies a task agent's prompts and code across "
        "generations, using score-proportional selection.",
    ),
    (
        re.compile(r"\bcapital (?:city )?of france\b"),
        "The capital of France is Paris.",
    ),
    (
        re.compile(r"\bfibonacci\b"),
        "Fibonacci sequence: F(0)=0, F(1)=1, F(n)=F(n-1)+F(n-2). F(10) is 55.",
    ),
    (
        re.compile(r"\bprime numbers?\b"),
        "A prime number is a natural number greater than 1 whose only positive "
        "divisors are 1 and itself.",
    ),
)


def _fallback_answer(query_lower: str):
    for pattern, answer in _FALLBACK_KNOWLEDGE:
        if pattern.search(query_lower):
            return answer
    return None


def _collect_topic_texts(topics) -> list:
    """Flatten DuckDuckGo RelatedTopics (which may contain nested groups)."""
    texts = []
    if not isinstance(topics, list):
        return texts
    for item in topics:
        if not isinstance(item, dict):
            continue
        text = item.get("Text")
        if isinstance(text, str) and text.strip():
            texts.append(text.strip())
        nested = item.get("Topics")
        if nested:
            texts.extend(_collect_topic_texts(nested))
    return texts


def web_search(query: str) -> str:
    """Search via the DuckDuckGo Instant Answer API.

    Live results are returned as "Live search result ...". If live search
    returns nothing useful, a narrowly matched predefined answer may be
    returned, always prefixed with an explicit fallback label.
    """
    if not isinstance(query, str) or not query.strip():
        return "Search error: Empty search query provided."

    query_clean = query.strip()
    failure = None  # Why live search did not produce a result, if known.

    try:
        with httpx.Client(timeout=_SEARCH_TIMEOUT_SECONDS) as client:
            resp = client.get(
                _SEARCH_URL,
                params={
                    "q": query_clean,
                    "format": "json",
                    "no_html": "1",
                    "skip_disambig": "1",
                },
            )
        if resp.status_code != 200:
            failure = f"search provider returned HTTP {resp.status_code}"
        else:
            data = resp.json()
            if not isinstance(data, dict):
                failure = "search provider returned an unexpected response format"
            else:
                abstract = data.get("AbstractText")
                if isinstance(abstract, str) and abstract.strip():
                    source = data.get("AbstractURL")
                    suffix = f" (Source: {source})" if isinstance(source, str) and source else ""
                    return f"Live search result for '{query_clean}': {abstract.strip()}{suffix}"

                snippets = _collect_topic_texts(data.get("RelatedTopics"))
                if snippets:
                    return (
                        f"Live search snippets for '{query_clean}': "
                        + " | ".join(snippets[:2])
                    )
    except httpx.TimeoutException:
        failure = "the search request timed out"
        logger.warning("web_search timed out for query %r", query_clean)
    except httpx.RequestError as exc:
        failure = f"the search request failed ({type(exc).__name__})"
        logger.warning("web_search request error for query %r: %s", query_clean, exc)
    except ValueError as exc:  # includes JSON decoding errors
        failure = "the search provider returned a malformed response"
        logger.warning("web_search malformed response for query %r: %s", query_clean, exc)

    if failure:
        logger.warning("web_search live lookup failed for %r: %s", query_clean, failure)

    fallback = _fallback_answer(query_clean.lower())
    if fallback:
        reason = f" Live search unavailable: {failure}." if failure else " Live search returned no results."
        return f"{_FALLBACK_LABEL}{reason} {fallback}"

    if failure:
        return (
            f"Search unavailable for '{query_clean}': {failure}. "
            "No results could be retrieved; try again later."
        )
    return (
        f"No useful live search results were found for '{query_clean}'. "
        "Try a more specific query or another search provider."
    )


# ---------------------------------------------------------------------------
# calculator
# ---------------------------------------------------------------------------

_MAX_INPUT_LENGTH = 500
_MAX_EXPRESSION_LENGTH = 200
_MAX_AST_NODES = 100
_MAX_MAGNITUDE = 1e100
_MAX_EXPONENT = 100

_BINARY_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_UNARY_OPS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}

_PROMPT_WORDS = re.compile(
    r"\bwhat is\b|\bwhat's\b|\bcalculate\b|\bcompute\b|\bplease\b|"
    r"\bcan you\b|\bcould you\b|\bgive me\b|\bthe answer to\b|"
    r"\banswer of\b|\bsolve\b"
)


def _normalize_expression(original: str) -> str:
    """Turn user text into a plain arithmetic string, or raise ValueError."""
    cleaned = original.lower()
    # Thousands separators only (1,000 -> 1000); other commas are left to fail.
    cleaned = re.sub(r"(?<=\d),(?=\d{3}(?!\d))", "", cleaned)
    cleaned = (
        cleaned.replace("×", "*")
        .replace("÷", "/")
        .replace("−", "-")
        .replace("^", "**")
    )

    # "25% of 200" / "25 percent of 200"
    cleaned = re.sub(
        r"(\d+(?:\.\d+)?)\s*(?:%|percent)\s*of\s*(\d+(?:\.\d+)?)",
        r"((\1/100)*\2)",
        cleaned,
    )

    cleaned = _PROMPT_WORDS.sub(" ", cleaned)
    cleaned = re.sub(r"\bmultiplied by\b|\btimes\b", "*", cleaned)
    cleaned = re.sub(r"\bdivided by\b", "/", cleaned)
    cleaned = re.sub(r"\bplus\b", "+", cleaned)
    cleaned = re.sub(r"\bminus\b", "-", cleaned)
    cleaned = re.sub(r"[?!]+$", "", cleaned).strip()

    # Standalone percentage: 25% -> (25/100). A % followed by an operand
    # (e.g. "10 % 3") is the modulo operator and is left alone.
    cleaned = re.sub(r"(\d+(?:\.\d+)?)\s*%(?!\s*[\d.(])", r"(\1/100)", cleaned)

    if not re.fullmatch(r"[0-9.+\-*/%()\s]+", cleaned):
        raise ValueError("Could not identify a complete arithmetic expression.")

    expr = re.sub(r"\s+", "", cleaned)
    if not expr or len(expr) > _MAX_EXPRESSION_LENGTH:
        raise ValueError("Expression is empty or too long.")
    return expr


def _evaluate(node):
    """Evaluate a whitelisted arithmetic AST node."""
    if isinstance(node, ast.Expression):
        return _evaluate(node.body)

    if isinstance(node, ast.Constant):
        if type(node.value) not in (int, float):
            raise ValueError("Only numeric values are allowed.")
        if isinstance(node.value, float) and not math.isfinite(node.value):
            raise ValueError("Invalid numeric value.")
        if abs(node.value) > _MAX_MAGNITUDE:
            raise ValueError("Number is too large.")
        return node.value

    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPS:
        return _UNARY_OPS[type(node.op)](_evaluate(node.operand))

    if isinstance(node, ast.BinOp) and type(node.op) in _BINARY_OPS:
        left = _evaluate(node.left)
        right = _evaluate(node.right)

        if isinstance(node.op, ast.Pow):
            if abs(right) > _MAX_EXPONENT:
                raise ValueError("Exponent is too large.")
            if abs(left) > 1e12 and right > 1:
                raise ValueError("Power calculation is too large.")

        result = _BINARY_OPS[type(node.op)](left, right)

        if isinstance(result, complex):
            raise ValueError("Complex results are not supported.")
        if isinstance(result, float) and not math.isfinite(result):
            raise ValueError("Result is not finite.")
        if abs(result) > _MAX_MAGNITUDE:
            raise ValueError("Result is too large.")
        return result

    raise ValueError("Unsupported arithmetic expression.")


def calculator(expression: str) -> str:
    """Evaluate basic arithmetic safely (AST whitelist; no eval/exec)."""
    if not isinstance(expression, str) or not expression.strip():
        return "Calculator Error: Please provide a mathematical expression."

    original = expression.strip()

    try:
        if len(original) > _MAX_INPUT_LENGTH:
            raise ValueError("Input is too long.")

        expr = _normalize_expression(original)
        tree = ast.parse(expr, mode="eval")
        if sum(1 for _ in ast.walk(tree)) > _MAX_AST_NODES:
            raise ValueError("Expression is too complex.")

        result = _evaluate(tree)
        if isinstance(result, float):
            if result.is_integer():
                result = int(result)
            else:
                result = float(f"{result:.12g}")  # hide binary float noise
        return f"Calculator Result: {expr} = {result}"

    except ZeroDivisionError:
        return "Calculator Error: Division by zero is not allowed."
    except (SyntaxError, ValueError, TypeError, OverflowError, RecursionError, MemoryError) as exc:
        return f"Calculator Error evaluating '{original}': {exc}"
    except Exception:
        logger.exception("Unexpected calculator failure for %r", original)
        return "Calculator Error: An unexpected calculation error occurred."


# ---------------------------------------------------------------------------
# python_interpreter
# ---------------------------------------------------------------------------

def python_interpreter(code: str) -> str:
    """Arbitrary Python execution is disabled until a secure sandbox exists."""
    if not isinstance(code, str) or not code.strip():
        return "Python Interpreter Error: No code was provided."

    return (
        "Python Interpreter Unavailable: Arbitrary code execution is disabled "
        "because this service does not have an isolated execution sandbox. "
        "Use the calculator tool for supported arithmetic operations."
    )


# ---------------------------------------------------------------------------
# data_analyzer
# ---------------------------------------------------------------------------

_MAX_ANALYZER_INPUT = 100_000
# Optional sign, then an integer, decimal, or leading-dot decimal. The
# lookbehind stops digits inside identifiers (gen_1, v2) or after a digit
# (the "-" in "1-2" is treated as a separator) from being picked up.
_NUMBER_PATTERN = re.compile(r"(?<![\w.])[-+]?(?:\d+(?:\.\d+)?|\.\d+)")


def _fmt(value: float) -> str:
    return f"{value:.6g}"


def data_analyzer(query_or_dataset: str) -> str:
    """Summarise numbers found in a text input.

    This extracts numeric tokens from free text and reports basic statistics.
    It does NOT parse CSV files or DataFrames and returns no project metrics.
    """
    if not isinstance(query_or_dataset, str):
        return "Data Analysis Error: Input must be a string of numeric values."
    if not query_or_dataset.strip():
        return "Data Analysis Error: No input was provided."
    if len(query_or_dataset) > _MAX_ANALYZER_INPUT:
        return "Data Analysis Error: Input is too large."

    try:
        numbers = [float(tok) for tok in _NUMBER_PATTERN.findall(query_or_dataset)]
        if not numbers:
            return (
                "Data Analysis Unavailable: No numeric data was found. "
                "Provide numerical values (e.g. '-5, 12, 3.14')."
            )

        arr = np.array(numbers, dtype=float)
        if not np.all(np.isfinite(arr)):
            return "Data Analysis Error: Input contains numbers that are too large."
        with np.errstate(all="ignore"):
            stats = [float(np.mean(arr)), float(np.std(arr))]
            if arr.size > 1:
                stats.append(float(np.std(arr, ddof=1)))
        if not all(math.isfinite(v) for v in stats):
            return "Data Analysis Error: Values are too large to analyze accurately."
        lines = [
            "Data Analysis Results (numbers extracted from the input text; "
            "this is not a CSV/DataFrame analysis):",
            f"- Count: {arr.size}",
            f"- Mean: {_fmt(float(np.mean(arr)))}",
            f"- Std Dev (population): {_fmt(float(np.std(arr)))}",
        ]
        if arr.size > 1:
            lines.append(f"- Std Dev (sample): {_fmt(float(np.std(arr, ddof=1)))}")
        lines.append(f"- Min: {_fmt(float(np.min(arr)))}")
        lines.append(f"- Max: {_fmt(float(np.max(arr)))}")
        return "\n".join(lines)
    except (ValueError, OverflowError, FloatingPointError) as exc:
        return f"Data Analysis Error: {exc}"
    except Exception:
        logger.exception("Unexpected data_analyzer failure")
        return "Data Analysis Error: An unexpected error occurred."


# Tool Registry map for dynamic tool binding
AVAILABLE_TOOLS = {
    "web_search": web_search,
    "calculator": calculator,
    "python_interpreter": python_interpreter,
    "data_analyzer": data_analyzer,
}
