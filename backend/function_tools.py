"""OpenAI Function Calling용 도구 정의"""

# 장소 검색 함수
SEARCH_PLACES_TOOL = {
    "type": "function",
    "function": {
        "name": "search_places",
        "description": "韓国の観光地、レストラン、カフェなどを検索します",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "検索クエリ (例: 明洞 カフェ)"
                },
                "region": {
                    "type": "string",
                    "description": "地域名 (例: ソウル、明洞、弘大)"
                },
                "area": {
                    "type": "string",
                    "description": "地域名の別名 (regionと同じ意味)"
                },
                "domain": {
                    "type": "string",
                    "enum": ["food", "shop", "his", "nat", "lei", "stay"],
                    "description": "カテゴリー"
                },
                "top_k": {
                    "type": "integer",
                    "description": "返却する件数 (1~10)",
                    "minimum": 1,
                    "maximum": 10
                }
            },
            "required": ["query"]
        }
    }
}

# 모든 도구 리스트
ALL_TOOLS = [
    SEARCH_PLACES_TOOL
]
