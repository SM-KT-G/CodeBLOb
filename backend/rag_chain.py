"""
RAG 체인 구성
LangChain 기반 RetrievalQA
"""
from __future__ import annotations

import asyncio
from copy import copy
from typing import Any, Dict, List, Optional, Sequence, TYPE_CHECKING

from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import BaseRetriever, Document
from langchain_openai import ChatOpenAI
from pydantic import ConfigDict, Field

from backend.utils.logger import setup_logger

if TYPE_CHECKING:  # pragma: no cover
    from backend.retriever import Retriever


logger = setup_logger()


# 프롬프트 템플릿 (일본어 응답 + 출처 명시)
PROMPT_TEMPLATE = """あなたは日本人観光客のための韓国観光ガイドチャットボットです。
以下のコンテキストを基に、質問に日本語で答えてください。
回答には必ず出典(ソース)を明記してください。

コンテキスト:
{context}

質問: {question}

回答（日本語）:"""


def create_rag_chain(
    llm_model: str = "gpt-4-turbo",
    retriever: BaseRetriever = None,
    temperature: float = 0.7,
) -> RetrievalQA:
    """
    RAG 체인 생성
    
    Args:
        llm_model: 사용할 LLM 모델명
        retriever: 문서 검색기 (PGVector retriever)
        temperature: LLM 생성 온도
    
    Returns:
        RetrievalQA 체인
    """
    if retriever is None:
        raise ValueError("Retriever가 제공되어야 합니다.")
    
    logger.info(f"RAG 체인 생성 중... (model={llm_model})")
    
    # LLM 초기화
    llm = ChatOpenAI(
        model=llm_model,
        temperature=temperature,
        request_timeout=15,
    )
    
    # 프롬프트 템플릿 생성
    prompt = PromptTemplate(
        template=PROMPT_TEMPLATE,
        input_variables=["context", "question"],
    )
    
    # RetrievalQA 체인 구성
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt},
    )
    
    logger.info("RAG 체인 생성 완료")
    
    return chain


def process_rag_response(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    RAG 체인 결과 후처리
    
    Args:
        result: RAG 체인 실행 결과
    
    Returns:
        처리된 결과 딕셔너리
    """
    # 답변 추출
    answer = result.get("result", "").strip()
    
    # 출처 문서 추출
    source_docs = result.get("source_documents", [])
    sources = []
    
    for doc in source_docs:
        # 문서 메타데이터에서 ID 추출
        metadata = doc.metadata
        doc_id = (
            metadata.get("document_id")
            or metadata.get("id")
            or metadata.get("source")
            or "Unknown"
        )
        if doc_id not in sources:
            sources.append(doc_id)
    
    return {
        "answer": answer,
        "sources": sources,
        "metadata": {
            "retrieved_count": len(source_docs),
        },
    }


def remove_parent_summary(docs: List[Document]) -> List[Document]:
    """
    Parent summary를 제거한 Document 리스트 반환.
    page_content에서 "質問:" 앞의 블록(요약)을 제거한다.
    """
    stripped = []
    for doc in docs:
        metadata_copy = copy(doc.metadata) if doc.metadata else {}
        page = doc.page_content or ""
        marker = "質問:"
        if marker in page:
            _, remainder = page.split(marker, 1)
            new_content = f"{marker}{remainder}".strip()
        else:
            new_content = page.strip()
        stripped.append(
            Document(
                page_content=new_content,
                metadata=metadata_copy,
            )
        )
    return stripped


class RetrieverAdapter(BaseRetriever):
    """
    LangChain BaseRetriever 인터페이스에 맞춰 custom Retriever를 감싸는 어댑터.
    요청별 필터(domain/area/expansion 등)를 안전하게 주입하기 위해
    인스턴스를 매 요청마다 생성한다.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
    retriever: Any
    top_k: int
    domain: Optional[str] = None
    area: Optional[str] = None
    expansion: bool = False
    variations: List[str] = Field(default_factory=list)
    include_parent_summary: bool = True

    def _query(self, query: str) -> List[Document]:
        return execute_retriever_query(
            retriever=self.retriever,
            query=query,
            top_k=self.top_k,
            domain=self.domain,
            area=self.area,
            expansion=self.expansion,
            variations=self.variations,
        )

    def _maybe_strip_parent_summary(self, docs: List[Document]) -> List[Document]:
        if self.include_parent_summary:
            return docs
        return remove_parent_summary(docs)

    def get_relevant_documents(
        self, query: str, *, run_manager: Optional[Any] = None
    ) -> List[Document]:
        docs = self._query(query)
        return self._maybe_strip_parent_summary(docs)

    async def aget_relevant_documents(
        self, query: str, *, run_manager: Optional[Any] = None
    ) -> List[Document]:
        loop = asyncio.get_running_loop()
        docs = await loop.run_in_executor(None, self._query, query)
        return self._maybe_strip_parent_summary(docs)



def execute_retriever_query(
    retriever: "Retriever",
    query: str,
    *,
    top_k: int,
    domain: Optional[str],
    area: Optional[str],
    expansion: bool,
    variations: Optional[Sequence[str]],
) -> List[Document]:
    """
    공통 검색 실행 헬퍼.
    expansion 여부에 따라 search / search_with_expansion을 호출한다.
    """
    domain_value = domain
    if expansion:
        return retriever.search_with_expansion(
            query=query,
            top_k=top_k,
            domain=domain_value,
            area=area,
            variations=list(variations or []),
        )
    return retriever.search(
        query=query,
        top_k=top_k,
        domain=domain_value,
        area=area,
    )
