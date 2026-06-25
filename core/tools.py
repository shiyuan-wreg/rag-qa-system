"""
工具函数定义
==========
为 Agent 提供可调用的真实工具：
- search_docs: 检索知识库
- execute_python: 安全执行 Python 代码
- read_file: 读取文件内容
- list_files: 列出目录文件
"""

import ast
import operator
import os
from typing import Any


# ==================== 安全 Python 执行器 ====================

_SAFE_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

_SAFE_NODES = (
    ast.Expression,
    ast.BinOp,
    ast.UnaryOp,
    ast.Constant,
    ast.Load,
    ast.Tuple,
    ast.List,
    ast.Dict,
    ast.Subscript,
    ast.Index,  # Python < 3.9
)


def _eval_node(node: ast.AST) -> Any:
    """递归求值 AST 节点，只允许安全操作。"""
    if isinstance(node, ast.Expression):
        return _eval_node(node.body)

    if isinstance(node, ast.Constant):
        return node.value

    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in _SAFE_OPS:
            raise ValueError(f"不支持的运算符: {op_type.__name__}")
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        return _SAFE_OPS[op_type](left, right)

    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in _SAFE_OPS:
            raise ValueError(f"不支持的运算符: {op_type.__name__}")
        operand = _eval_node(node.operand)
        return _SAFE_OPS[op_type](operand)

    if isinstance(node, ast.Tuple):
        return tuple(_eval_node(e) for e in node.elts)

    if isinstance(node, ast.List):
        return [_eval_node(e) for e in node.elts]

    if isinstance(node, ast.Dict):
        return {
            _eval_node(k): _eval_node(v)
            for k, v in zip(node.keys, node.values)
        }

    raise ValueError(f"不支持的 AST 节点类型: {type(node).__name__}")


def safe_execute_python(code: str) -> str:
    """
    安全执行一段受限的 Python 表达式。

    仅支持：数字运算、列表/字典字面量、基本索引访问。
    不支持：函数调用、变量引用、导入语句等。
    """
    code = code.strip()
    if not code:
        return "Error: empty code"

    try:
        tree = ast.parse(code, mode='eval')
        result = _eval_node(tree)
        return str(result)
    except SyntaxError as e:
        return ("Error: 本工具只支持单个算术表达式(如 2+3*4),不支持 def/print/import/语句/多行代码。"
                "请不要再调用本工具,直接用文字回答用户。")
    except Exception as e:
        return f"Error: execution failed - {e}"


# ==================== 文件工具 ====================

def read_file(path: str) -> str:
    """读取指定文本文件内容。"""
    if not os.path.exists(path):
        return f"Error: file not found '{path}'"

    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            # 避免返回过长内容
            if len(content) > 3000:
                content = content[:3000] + "\n... (content truncated)"
            return content
    except Exception as e:
        return f"Error: read failed - {e}"


def list_files(directory: str = ".") -> str:
    """列出指定目录下的文件和子目录。"""
    if not os.path.exists(directory):
        return f"Error: directory not found '{directory}'"

    try:
        items = os.listdir(directory)
        if not items:
            return f"Directory '{directory}' is empty"

        lines = [f"Contents of '{directory}':"]
        for item in sorted(items):
            item_path = os.path.join(directory, item)
            item_type = "[DIR]" if os.path.isdir(item_path) else "[FILE]"
            lines.append(f"  {item_type} {item}")
        return "\n".join(lines)
    except Exception as e:
        return f"Error: list failed - {e}"


# ==================== 工具 Schema ====================

TOOL_MAP = {
    "execute_python": safe_execute_python,
    "read_file": read_file,
    "list_files": list_files,
}

# search_docs 会由 rag_tool.py 动态注册

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_docs",
            "description": "从知识库中检索与问题相关的文档片段，用于回答需要依据文档内容的问题",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "检索查询，应是具体的问题或关键词"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "execute_python",
            "description": "纯算术计算器：只能计算单个算术表达式(数字四则运算、列表/字典字面量、索引)。不能定义函数、不能用 print、不能写多行代码或语句。只在需要精确数字计算时调用,其它问题请直接用文字回答。",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "单个算术表达式,例如 '15 + 27 * 3' 或 '[1, 2, 3] + [4, 5]'。禁止 def/print/import/多行。"
                    }
                },
                "required": ["code"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "读取指定文本文件的内容",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "文件路径，例如 'docs/python_guide.txt'"
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "列出指定目录下的文件和子目录",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "目录路径，默认为当前目录 '.'"
                    }
                },
                "required": []
            }
        }
    },
]
