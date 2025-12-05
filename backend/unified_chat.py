"""
UnifiedChatHandler - Function Calling 통합 처리
일반 대화, RAG 검색, 여행 일정을 하나로 통합
"""
import json
from typing import Dict, Any, List, Optional
from backend.llm_base import LLMClient
from backend.retriever import Retriever
from backend.itinerary import ItineraryPlanner
from backend.function_tools import ALL_TOOLS
from backend.schemas import ChatRequest, ItineraryStructuredResponse
from backend.utils.logger import setup_logger


logger = setup_logger()


class UnifiedChatHandler:
    """통합 채팅 핸들러 - Function Calling 사용"""
    
    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        retriever: Optional[Retriever] = None,
        itinerary_recommender: Optional[ItineraryPlanner] = None
    ):
        """
        Args:
            llm_client: LLM 클라이언트
            retriever: RAG 검색기
            itinerary_recommender: 일정 추천기
        """
        self.llm = llm_client or LLMClient()
        self.retriever = retriever
        self.itinerary = itinerary_recommender
        
        logger.info("UnifiedChatHandler 초기화 완료")
    
    async def initialize(self):
        """비동기 초기화"""
        # 필요시 여기서 DB 연결 등 초기화
        pass
    
    async def close(self):
        """리소스 정리"""
        pass

    def _infer_area_from_text(self, text: str) -> Optional[str]:
        """간단한 지역 키워드 추론 (실험적)"""
        if not text:
            return None
        text_lower = text.lower()
        candidates = [
            ("서울", "서울"),
            ("ソウル", "서울"),
            ("seoul", "서울"),
            ("부산", "부산"),
            ("釜山", "부산"),
            ("busan", "부산"),
            ("제주", "제주"),
            ("濟州", "제주"),
            ("jeju", "제주"),
            ("대전", "대전"),
            ("daejeon", "대전"),
            ("대구", "대구"),
            ("daegu", "대구"),
            ("광주", "광주"),
            ("gwangju", "광주"),
            ("인천", "인천"),
            ("incheon", "인천"),
        ]
        for key, area in candidates:
            if key in text or key in text_lower:
                return area
        return None
    
    async def handle_chat(self, request: ChatRequest) -> Dict[str, Any]:
        """
        통합 채팅 처리 - Function Calling으로 의도 파악
        
        Args:
            request: 채팅 요청
        
        Returns:
            응답 dict
        """
        try:
            # 1. 컨텍스트 구성
            messages = self._build_messages(request)
            
            # 2. Function Calling 요청
            logger.info("Function Calling 요청 수신")
            
            completion = self.llm.client.chat.completions.create(
                model=self.llm.model,
                messages=messages,
                tools=ALL_TOOLS,
                tool_choice="auto",
                temperature=0.7
            )
            
            response_message = completion.choices[0].message
            
            # 3. Function Call이 있는지 확인
            if response_message.tool_calls:
                tool_call = response_message.tool_calls[0]
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                # 원문 텍스트를 전달해 쿼리/영역 fallback에 활용
                arguments.setdefault("user_text", request.text)
                
                logger.info(f"Function Called: {function_name}, args={arguments}")
                
                # 4. Function 실행
                if function_name == "search_places":
                    response = await self._handle_search_places(arguments)
                else:
                    response = {
                        "message": "旅行日程の作成は /recommend/itinerary を呼び出してください。",
                    }
            else:
                # 일반 대화
                response = self._handle_general_chat(response_message.content)
            
            # 5. chat_completion_id 추가
            response["chat_completion_id"] = completion.id
            
            return response
        
        except Exception as e:
            logger.error(f"채팅 처리 실패: {e}")
            return {
                "message": f"처리 중 오류가 발생했습니다: {str(e)}"
            }
    
    def _build_messages(self, request: ChatRequest) -> List[Dict[str, str]]:
        """
        메시지 컨텍스트 구성
        
        Args:
            request: 채팅 요청
        
        Returns:
            메시지 리스트
        """
        messages = [
            {
                "role": "system",
                "content": """あなたは韓国旅行の専門アシスタントです。常に日本語で丁寧に回答してください。ツールを呼ぶとき 아래 지침을 따르세요:
1) 위치/지역 추출: 한국어·일본어·영어로 등장하는 도시/지역(서울, 釜山, 제주 등)을 모두 감지해 area/region에 설정합니다. 없으면 user_text에서 추론합니다.
2) 검색 쿼리: query에는 원문 텍스트를 그대로 사용하고, top_k는 3으로 설정합니다.
3) 도메인: 요청에 음식/카페/쇼핑/자연/역사 등이 있으면 domain에 반영합니다(없으면 비워둠).
4) 정보 부족: 지역이 전혀 언급되지 않았고 추론도 어렵다면, 먼저 짧게 어느 지역을 원하는지 물어봅니다.
5) 응답 형식: /chat 응답에는 message와 places 배열(이름, 지역, document_id)만 포함되도록 도와주세요."""
            }
        ]

        # 현재 메시지
        messages.append({"role": "user", "content": request.text})
        
        return messages
    
    def _handle_general_chat(self, content: str) -> Dict[str, Any]:
        """일반 대화 처리"""
        return {
            "message": content
        }
    
    async def _handle_search_places(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """장소 검색 처리"""
        if not self.retriever:
            return {
                "message": "検索機能が利用できません"
            }
        
        try:
            user_text = args.get("user_text") or ""
            query = (args.get("query") or user_text).strip()
            domain = args.get("domain")
            # area가 없으면 region을 area로 사용
            area = args.get("area") or args.get("region")
            if not area:
                area = self._infer_area_from_text(user_text)
            top_k = args.get("top_k", 3)

            if not query or len(query) < 2:
                return {
                    "message": "検索クエリをもう少し具体的に入力してください。"
                }
            
            # RAG 검색
            results = self.retriever.search(
                query=query,
                top_k=top_k,
                domain=domain,
                area=area
            )
            
            # 응답 생성
            if results:
                places = [
                    {
                        # place_name/title 우선, 없으면 name/food_name
                        "name": r.metadata.get("place_name")
                        or r.metadata.get("title")
                        or r.metadata.get("name")
                        or r.metadata.get("food_name")
                        or "",
                        "description": r.page_content[:200],
                        "area": r.metadata.get("area")
                        or r.metadata.get("sigungu")
                        or (area or ""),
                        "document_id": r.metadata.get("document_id", "")
                    }
                    for r in results
                ]
                
                message = f"{len(places)}件の場所が見つかりました。"
                
                return {
                    "message": message,
                    "places": places
                }
            else:
                return {
                    "message": "申し訳ございません。該当する場所が見つかりませんでした。",
                    "places": []
                }
        
        except Exception as e:
            logger.error(f"검색 실패: {e}")
            return {
                "message": f"検索中にエラーが発生しました: {str(e)}"
            }
    
    async def _handle_create_itinerary(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """여행 일정 생성 처리"""
        try:
            region = args.get("region")
            duration_days = args.get("duration_days")
            themes = args.get("themes", [])
            domains = args.get("domains", ["food", "shop"])
            
            # Structured Outputs로 일정 생성
            prompt = f"""
{region}の{duration_days}日間の旅行プランを作成してください。

テーマ: {', '.join(themes) if themes else 'なし'}
興味のあるカテゴリー: {', '.join(domains)}

詳細な日程を作成してください。
"""
            
            system_prompt = """あなたは親切な旅行プランナーです。
ユーザーのリクエストに基づいて、詳細で実用的な旅行プランを作成します。
プランには各日の具体的な訪問場所、時間帯、活動内容を含めてください。
最初に簡単な挨拶と説明を追加してください。"""
            
            result = self.llm.generate_structured(
                prompt=prompt,
                response_format=ItineraryStructuredResponse,
                system_prompt=system_prompt
            )
            
            # Pydantic 모델 → dict
            return {
                "message": result.message,
                "itinerary": {
                    "title": result.itinerary.title,
                    "summary": result.itinerary.summary,
                    "days": [
                        {
                            "day": day.day,
                            "segments": [
                                {
                                    "time": seg.time,
                                    "place_name": seg.place_name,
                                    "description": seg.description,
                                    "place_id": getattr(seg, "document_id", None)
                                }
                                for seg in day.segments
                            ]
                        }
                        for day in result.itinerary.days
                    ],
                    "highlights": result.itinerary.highlights
                }
            }
        
        except Exception as e:
            logger.error(f"일정 생성 실패: {e}")
            return {
                "message": f"プラン作成中にエラーが発生しました: {str(e)}"
            }
