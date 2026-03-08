"""LCEL RAG chain: hybrid retriever (vector + BM25) and ainvoke."""
from typing import Any

from langchain_openai import ChatOpenAI
try:
    from openai import APITimeoutError as _OpenAITimeout
except ImportError:
    try:
        from openai import Timeout as _OpenAITimeout  # legacy
    except ImportError:
        _OpenAITimeout = None
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from langchain_core.documents import Document

from backend.core.config import settings
from backend.core.exceptions import OpenAITimeoutError


def _format_docs(docs: list[Document]) -> str:
    return "\n\n".join(doc.page_content or "" for doc in docs)


def build_rag_chain(vectorstore: Any, bm25_retriever: BM25Retriever) -> Any:
    """
    Build LCEL runnable: input {"input": str} -> output {"answer": str, "context": list[Document]}.
    Uses EnsembleRetriever (vector + BM25) and async ainvoke.
    """
    vector_retriever = vectorstore.as_retriever(
        search_kwargs={"k": settings.vector_retriever_k}
    )
    ensemble_retriever = EnsembleRetriever(
        retrievers=[vector_retriever, bm25_retriever],
        weights=[settings.ensemble_weight_vector, settings.ensemble_weight_bm25],
    )
    llm = ChatOpenAI(
        model=settings.llm_model,
        temperature=settings.llm_temperature,
        openai_api_key=settings.openai_api_key or None,
    )
    prompt = ChatPromptTemplate.from_template("""
請根據以下內容回答問題。如果無法從內容中找到答案，請回答「我無法從提供的內容中找到相關資訊」。
內容：{context}
問題：{input}
""")

    async def _retrieve_and_generate(x: dict[str, Any]) -> dict[str, Any]:
        question = x.get("input", "")
        try:
            docs = await ensemble_retriever.ainvoke(question)
            formatted = _format_docs(docs)
            answer = await (prompt | llm | StrOutputParser()).ainvoke({
                "context": formatted,
                "input": question,
            })
            return {"answer": answer, "context": docs}
        except Exception as e:
            if _OpenAITimeout is not None and isinstance(e, _OpenAITimeout):
                raise OpenAITimeoutError(str(e)) from e
            raise

    return RunnableLambda(_retrieve_and_generate)


async def aquery(question: str, chain: Any) -> dict:
    """Run RAG chain asynchronously. Returns dict with 'answer' and 'context' (list of Documents)."""
    return await chain.ainvoke({"input": question})
