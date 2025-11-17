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
                "domain": {
                    "type": "string",
                    "enum": ["food", "shop", "his", "nat", "lei", "stay"],
                    "description": "カテゴリー"
                }
            },
            "required": ["query"]
        }
    }
}

# 여행 일정 생성 함수
CREATE_ITINERARY_TOOL = {
    "type": "function",
    "function": {
        "name": "create_itinerary",
        "description": "韓国旅行の日程プランを作成します",
        "parameters": {
            "type": "object",
            "properties": {
                "region": {
                    "type": "string",
                    "description": "旅行地域 (例: ソウル、釜山)"
                },
                "duration_days": {
                    "type": "integer",
                    "description": "旅行日数",
                    "minimum": 1,
                    "maximum": 7
                },
                "domains": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["food", "shop", "his", "nat", "lei", "stay"]
                    },
                    "description": "興味のあるカテゴリーリスト"
                },
                "themes": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "旅行テーマ (例: インスタ映え、グルメ、歴史)"
                }
            },
            "required": ["region", "duration_days"]
        }
    }
}

# 모든 도구 리스트
ALL_TOOLS = [
    SEARCH_PLACES_TOOL,
    CREATE_ITINERARY_TOOL
]
