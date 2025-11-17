"""
LLM 기본 클라이언트
OpenAI API 래퍼
"""
import os
import asyncio
from typing import List, Dict, Any, Optional, Type, TypeVar
from openai import OpenAI, AsyncOpenAI
from pydantic import BaseModel

from backend.utils.logger import setup_logger, log_exception


logger = setup_logger()

# Pydantic 제네릭 타입
T = TypeVar("T", bound=BaseModel)


class LLMClient:
    """
    OpenAI LLM 클라이언트
    타임아웃 및 재시도 로직 포함
    """
    
    def __init__(
        self,
        model_name: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: int = 15,
    ):
        """
        초기화
        
        Args:
            model_name: 사용할 OpenAI 모델명 (None이면 환경변수에서 로드)
            api_key: OpenAI API 키 (None이면 환경변수에서 로드)
            timeout: API 호출 타임아웃 (초)
        """
        self.model = model_name or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.timeout = timeout
        
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")
        
        self.client = OpenAI(api_key=api_key)
        self.async_client = AsyncOpenAI(api_key=api_key)
        
        logger.info(f"LLM 클라이언트 초기화: model={self.model}, timeout={timeout}s")
    
    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        동기 방식으로 응답 생성
        
        Args:
            messages: 대화 메시지 리스트
            temperature: 생성 온도 (0~2)
            max_tokens: 최대 토큰 수
        
        Returns:
            생성된 텍스트
        """
        try:
            logger.info(f"LLM 생성 요청: {len(messages)} 메시지, model={self.model}")
            
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=self.timeout,
            )
            
            response = completion.choices[0].message.content.strip()
            logger.info(f"LLM 응답 생성 완료: {len(response)} 문자")
            
            return response
        
        except Exception as e:
            log_exception(
                e,
                context={
                    "model": self.model,
                    "messages_count": len(messages),
                },
                logger=logger,
            )
            return f"[오류] 응답 생성 실패: {str(e)}"
    
    async def agenerate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        비동기 방식으로 응답 생성 (타임아웃 포함)
        
        Args:
            messages: 대화 메시지 리스트
            temperature: 생성 온도 (0~2)
            max_tokens: 최대 토큰 수
        
        Returns:
            생성된 텍스트
        """
        try:
            logger.info(f"LLM 비동기 생성 요청: {len(messages)} 메시지")
            
            async with asyncio.timeout(self.timeout):
                completion = await self.async_client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            
            response = completion.choices[0].message.content.strip()
            logger.info(f"LLM 비동기 응답 생성 완료: {len(response)} 문자")
            
            return response
        
        except asyncio.TimeoutError:
            error_msg = f"LLM 요청 타임아웃 ({self.timeout}초 초과)"
            logger.error(error_msg)
            return f"[오류] {error_msg}"
        
        except Exception as e:
            log_exception(
                e,
                context={
                    "model": self.model,
                    "messages_count": len(messages),
                },
                logger=logger,
            )
            return f"[오류] 응답 생성 실패: {str(e)}"
    
    def generate_structured(
        self,
        prompt: str,
        response_format: Type[T],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
    ) -> T:
        """
        Structured Outputs로 100% JSON 보장 응답 생성
        
        Args:
            prompt: 사용자 프롬프트
            response_format: Pydantic 모델 (응답 스키마)
            system_prompt: 시스템 프롬프트 (선택)
            temperature: 생성 온도
        
        Returns:
            Pydantic 모델 인스턴스
        """
        try:
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            messages.append({"role": "user", "content": prompt})
            
            logger.info(f"Structured Outputs 요청: model={response_format.__name__}")
            
            completion = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=messages,
                response_format=response_format,
                temperature=temperature,
                timeout=self.timeout,
            )
            
            result = completion.choices[0].message.parsed
            logger.info(f"Structured Outputs 생성 완료: {type(result).__name__}")
            
            return result
        
        except Exception as e:
            log_exception(
                e,
                context={
                    "model": self.model,
                    "response_format": response_format.__name__,
                },
                logger=logger,
            )
            raise
