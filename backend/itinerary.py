"""
Itinerary recommendation helper
"""
from __future__ import annotations

from collections import OrderedDict
from typing import Dict, List, Sequence

from langchain.schema import Document

from backend.retriever import Retriever
from backend.schemas import (
    ItineraryPlan,
    ItineraryRecommendationRequest,
    ItinerarySegment,
    DayPlan,
)


class ItineraryPlanner:
    """간단한 추천 일정 생성기 (LLM 연동 이전 버전)"""

    def __init__(self, retriever: Retriever):
        self.retriever = retriever

    def recommend(
        self,
        request: ItineraryRecommendationRequest,
    ) -> Dict[str, List[ItineraryPlan]]:
        """
        요청 정보를 바탕으로 추천 일정 생성
        """
        candidates = self._gather_candidates(request)
        itineraries = self._build_itineraries(request, candidates)
        metadata = {
            "generated_count": len(itineraries),
            "duration_days": request.duration_days,
            "region": request.region,
            "domains": [d.value for d in request.domains],
            "themes": request.themes,
            "transport_mode": request.transport_mode,
            "budget_level": request.budget_level,
            "expansion": request.expansion,
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

    def _build_itineraries(
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
