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
                
                logger.info(f"Function Called: {function_name}, args={arguments}")
                
                # 4. Function 실행
                if function_name == "search_places":
                    response = await self._handle_search_places(arguments)
                elif function_name == "create_itinerary":
                    response = await self._handle_create_itinerary(arguments)
                else:
                    response = {
                        "message": f"Unknown function: {function_name}"
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
                "content": """あなたは韓国旅行の専門アシスタントです。
以下のことができます:
1. 観光地、レストラン、カフェなどの情報検索
2. 旅行プランの作成
3. 一般的な旅行相談

ユーザーの意図を理解して、適切な機能を使用してください。"""
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
            query = args.get("query")
            domain = args.get("domain")
            area = args.get("area")
            top_k = args.get("top_k", 5)
            
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
                        "name": r.metadata.get("name", r.metadata.get("food_name", "")),
                        "description": r.page_content[:200],
                        "area": r.metadata.get("sigungu", ""),
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
