"""Unit tests for tool functions"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.tools import safe_execute_python, read_file, list_files


def test_safe_execute_python():
    assert safe_execute_python("2 + 3 * 4") == "14"
    assert safe_execute_python("(15 + 27) * 3") == "126"
    assert safe_execute_python("[1, 2, 3] + [4, 5]") == "[1, 2, 3, 4, 5]"
    assert safe_execute_python("__import__('os').system('ls')").startswith("Error:")
    assert safe_execute_python("open('test.txt')").startswith("Error:")
    print("[OK] safe_execute_python passed")


def test_read_file():
    result = read_file("docs/python_guide.txt")
    assert not result.startswith("Error:")
    assert len(result) > 0

    result = read_file("not_exist.txt")
    assert result.startswith("Error:")
    print("[OK] read_file passed")


def test_list_files():
    result = list_files("docs")
    assert not result.startswith("Error:")
    assert "[FILE]" in result or "[DIR]" in result

    result = list_files("not_exist_dir")
    assert result.startswith("Error:")
    print("[OK] list_files passed")


if __name__ == "__main__":
    test_safe_execute_python()
    test_read_file()
    test_list_files()
    print("\nAll tool tests passed!")
