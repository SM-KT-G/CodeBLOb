"""Function tools 구성 테스트"""
from backend.function_tools import ALL_TOOLS


def test_all_tools_contains_only_search_places():
    """ALL_TOOLS는 검색 도구 하나만 포함해야 한다."""
    tool_names = [t["function"]["name"] for t in ALL_TOOLS]
    assert tool_names == ["search_places"]
