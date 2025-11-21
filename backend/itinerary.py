"""
Itinerary recommendation helper
"""
from __future__ import annotations

import json
import os
from collections import OrderedDict
from typing import Any, Dict, List, Sequence

from langchain.prompts import ChatPromptTemplate
from langchain.schema import Document
from langchain_openai import ChatOpenAI

from backend.retriever import Retriever
from backend.schemas import (
    ItineraryPlan,
    ItineraryRecommendationRequest,
    ItinerarySegment,
    DayPlan,
)
from backend.utils.logger import setup_logger


logger = setup_logger()


class ItineraryPlanner:
    """Query Expansion + LLM 기반 추천 일정 생성기"""

    def __init__(self, retriever: Retriever, llm_model: str = "gpt-4o"):
        self.retriever = retriever
        self.llm_model = llm_model

    def recommend(
        self,
        request: ItineraryRecommendationRequest,
    ) -> Dict[str, List[ItineraryPlan]]:
        """
        요청 정보를 바탕으로 추천 일정 생성
        """
        candidates = self._gather_candidates(request)
        itineraries: List[ItineraryPlan] = []
        generator = "rule"

        if candidates:
            try:
                itineraries = self._generate_with_llm(request, candidates)
                if itineraries:
                    generator = "llm"
            except Exception as exc:  # pylint: disable=broad-except
                logger.warning("LLM itinerary generation failed: %s", exc)

        if not itineraries:
            itineraries = self._build_rule_based_itineraries(request, candidates)

        metadata = {
            "generated_count": len(itineraries),
            "duration_days": request.duration_days,
            "region": request.region,
            "domains": [d.value for d in request.domains],
            "themes": request.themes,
            "transport_mode": request.transport_mode,
            "budget_level": request.budget_level,
            "expansion": request.expansion,
            "generator": generator,
        }
        if request.expansion:
            metadata["expansion_metrics"] = getattr(
                self.retriever, "last_expansion_metrics", None
            )

        return {
            "itineraries": itineraries,
            "metadata": metadata,
        }

    def _gather_candidates(
        self,
        request: ItineraryRecommendationRequest,
    ) -> List[Document]:
        """도메인별 후보 문서를 수집"""
        per_domain = max(3, request.duration_days * 3)
        docs_by_id: "OrderedDict[str, Document]" = OrderedDict()

        def add_docs(documents):
            for doc in documents:
                doc_id = doc.metadata.get("document_id") or doc.metadata.get("documentId")
                if not doc_id:
                    doc_id = str(hash(doc.page_content))
                if doc_id not in docs_by_id:
                    docs_by_id[doc_id] = doc

        for domain in request.domains:
            query = f"{request.region} {domain.value}"
            search_kwargs = {
                "query": query,
                "top_k": per_domain,
                "domain": domain.value,
                "area": request.region,
            }
            if request.expansion:
                docs = self.retriever.search_with_expansion(**search_kwargs)
            else:
                docs = self.retriever.search(**search_kwargs)
            add_docs(docs)

        return list(docs_by_id.values())

    def _build_rule_based_itineraries(
        self,
        request: ItineraryRecommendationRequest,
        docs: Sequence[Document],
    ) -> List[ItineraryPlan]:
        """수집된 문서로 간단한 일정안을 생성"""
        if not docs:
            return []

        preferred = set(request.preferred_places or [])
        avoid = set(request.avoid_places or [])

        filtered = [
            doc
            for doc in docs
            if doc.metadata.get("document_id") not in avoid
        ]

        # preferred 문서를 우선 배치
        preferred_docs = [
            doc
            for doc in filtered
            if doc.metadata.get("document_id") in preferred
        ]
        others = [
            doc
            for doc in filtered
            if doc.metadata.get("document_id") not in preferred
        ]
        ordered_docs = preferred_docs + others
        domain_labels = sorted(
            {
                (doc.metadata or {}).get("domain")
                for doc in ordered_docs
                if (doc.metadata or {}).get("domain")
            }
        )
        domain_text = ", ".join(domain_labels) if domain_labels else "mixed"

        num_itineraries = min(3, max(1, len(ordered_docs) // request.duration_days))
        itineraries: List[ItineraryPlan] = []
        idx = 0

        for i in range(num_itineraries):
            day_plans: List[DayPlan] = []
            highlights: List[str] = []

            for day in range(1, request.duration_days + 1):
                segments: List[ItinerarySegment] = []
                for _ in range(2):  # 하루에 최대 2개 장소
                    if idx >= len(ordered_docs):
                        break
                    doc = ordered_docs[idx]
                    idx += 1
                    meta = doc.metadata or {}
                    place_name = meta.get("place_name") or meta.get("title") or "추천 장소"
                    highlights.append(place_name)
                    segments.append(
                        ItinerarySegment(
                            time=None,
                            place_name=place_name,
                            description=doc.page_content[:180],
                            document_id=meta.get("document_id"),
                            source_url=meta.get("source_url"),
                            area=meta.get("area"),
                            notes=f"domain={meta.get('domain')}",
                        )
                    )
                if segments:
                    day_plans.append(
                        DayPlan(
                            day=day,
                            segments=segments,
                        )
                    )

            if not day_plans:
                break

            itinerary = ItineraryPlan(
                title=f"{request.region} {request.duration_days}일 추천 #{i + 1}",
                summary=f"{request.region}에서 {domain_text} 테마로 구성된 {request.duration_days}일 일정",
                days=day_plans,
                highlights=highlights[:5],
                estimated_budget=request.budget_level or "standard",
                metadata={
                    "domains": [d.value for d in request.domains],
                    "region": request.region,
                },
            )
            itineraries.append(itinerary)

        return itineraries

    def _generate_with_llm(
        self,
        request: ItineraryRecommendationRequest,
        docs: Sequence[Document],
    ) -> List[ItineraryPlan]:
        """LLM에 후보 장소를 전달해 추천 일정을 생성"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY가 설정되지 않아 LLM을 사용할 수 없습니다.")

        if not docs:
            return []

        candidates = self._format_candidates(docs[: min(12, len(docs))])

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "あなたは日本人旅行者のための韓国旅行プランナーです。"
                    "複数の旅行日程オプションをJSON形式で生成してください。JSON以外のコメントは絶対に追加しないでください。",
                ),
                (
                    "user",
                    self._build_prompt(request, candidates),
                ),
            ]
        )

        llm = ChatOpenAI(
            model=self.llm_model,
            temperature=0.4,
            max_tokens=2000,
        )

        response = llm.invoke(prompt.format_messages())  # type: ignore[arg-type]
        content = response.content if hasattr(response, "content") else str(response)
        payload = self._parse_json_response(content)
        itineraries_data = payload.get("itineraries", [])
        itineraries: List[ItineraryPlan] = []

        for item in itineraries_data:
            itineraries.append(ItineraryPlan(**item))

        return itineraries

    def _format_candidates(self, docs: Sequence[Document]) -> str:
        lines = []
        for doc in docs:
            meta = doc.metadata or {}
            place = meta.get("place_name") or meta.get("title") or "장소"
            doc_id = meta.get("document_id") or "(unknown)"
            domain = meta.get("domain") or ""
            summary = (meta.get("parent_summary") or doc.page_content).strip().replace("\n", " ")
            lines.append(
                f"- id:{doc_id} name:{place} domain:{domain} summary:{summary[:220]}"
            )
        return "\n".join(lines)

    def _build_prompt(
        self,
        request: ItineraryRecommendationRequest,
        candidates: str,
    ) -> str:
        themes = ", ".join(request.themes) if request.themes else "なし"
        preferred = ", ".join(request.preferred_places) if request.preferred_places else "なし"
        avoid = ", ".join(request.avoid_places) if request.avoid_places else "なし"

        return f"""
以下の条件を満たす旅行日程を{min(3, max(1, request.duration_days))}個JSON形式で作成してください。

リクエスト情報:
- 地域: {request.region}
- ドメイン: {', '.join(d.value for d in request.domains)}
- 日程: {request.duration_days}日
- テーマ: {themes}
- 移動手段: {request.transport_mode or '指定なし'}
- 予算: {request.budget_level or 'standard'}
- 必須訪問地: {preferred}
- 除外地: {avoid}

候補スポット:
{candidates}

JSON形式:
{{
  "itineraries": [
    {{
      "title": "string",
      "summary": "string",
      "days": [
        {{
          "day": 1,
          "segments": [
            {{
              "time": "午前",
              "place_name": "string",
              "description": "string",
              "document_id": "J_xxx",
              "source_url": "string",
              "area": "string",
              "notes": "string"
            }}
          ]
        }}
      ],
      "highlights": ["string"],
      "estimated_budget": "string",
      "metadata": {{}}
    }}
  ]
}}

必ず上記のJSON形式のみを出力してください（コードブロック、コメント、説明は禁止）。dayの数は{request.duration_days}日と同じにし、各dayには最大2つのsegmentのみを含めてください。
"""

    def _parse_json_response(self, content: str) -> Dict[str, Any]:
        text = content.strip()
        if text.startswith("```"):
            text = text.strip("`")
            if text.startswith("json"):
                text = text[4:].strip()
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            text = text[start : end + 1]
        return json.loads(text)
