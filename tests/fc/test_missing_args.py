"""Unit tests for FC missing-required-argument detection"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backends.fc_app.main import missing_required_args


def test_missing_returns_absent_required():
    # set_reminder 需要 content + time,这里缺 time
    assert missing_required_args("set_reminder", {"content": "开会"}) == ["time"]
    print("[OK] detects absent required arg")


def test_missing_treats_empty_as_missing():
    assert missing_required_args("set_reminder", {"content": "开会", "time": ""}) == ["time"]
    print("[OK] empty string counts as missing")


def test_missing_none_when_complete():
    assert missing_required_args("get_weather", {"city": "北京"}) == []
    print("[OK] complete args -> no missing")


def test_missing_unknown_tool_empty():
    assert missing_required_args("no_such_tool", {}) == []
    print("[OK] unknown tool -> empty")


if __name__ == "__main__":
    test_missing_returns_absent_required()
    test_missing_treats_empty_as_missing()
    test_missing_none_when_complete()
    test_missing_unknown_tool_empty()
    print("\nAll FC missing-args tests passed!")
