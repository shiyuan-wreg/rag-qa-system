import re
from app.tools.registry import registry

SAFE_CHARS = re.compile(r"^[0-9+\-*/().\s]+$")

def calculate(expression: str) -> str:
    """安全计算数学表达式。"""
    try:
        cleaned = expression.strip()
        if not SAFE_CHARS.match(cleaned):
            return "错误：表达式包含非法字符"
        result = eval(cleaned, {"__builtins__": {}}, {})
        return f"计算结果：{result}"
    except Exception as e:
        return f"计算失败：{str(e)}"

registry.register("calculate", calculate)
