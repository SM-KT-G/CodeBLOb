"""
RAG 체인 구성
LangChain 기반 RetrievalQA
"""
from typing import Dict, List, Any
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import BaseRetriever
from langchain_openai import ChatOpenAI

from utils.logger import setup_logger


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
        doc_id = metadata.get("id") or metadata.get("source", "Unknown")
        if doc_id not in sources:
            sources.append(doc_id)
    
    return {
        "answer": answer,
        "sources": sources,
    }
