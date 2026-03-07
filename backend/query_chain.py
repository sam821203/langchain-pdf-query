# LangChain 查詢鏈邏輯
from langchain_openai import ChatOpenAI
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.retrievers import EnsembleRetriever

def create_query_chain(vectorstore, bm25_retriever):
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    vector_retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
    ensemble_retriever = EnsembleRetriever(
        retrievers=[vector_retriever, bm25_retriever],
        weights=[0.5, 0.5],
    )

    prompt = ChatPromptTemplate.from_template("""
    請根據以下內容回答問題。如果無法從內容中找到答案，請回答「我無法從提供的內容中找到相關資訊」。
    內容：{context}
    問題：{input}
    """)

    document_chain = create_stuff_documents_chain(llm, prompt)
    return create_retrieval_chain(ensemble_retriever, document_chain)
