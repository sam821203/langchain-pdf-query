# LangChain 查詢鏈邏輯
from langchain_openai import ChatOpenAI
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain

def create_query_chain(vectorstore):
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

    prompt = ChatPromptTemplate.from_template("""
    請根據以下內容回答問題。如果無法從內容中找到答案，請回答「我無法從提供的內容中找到相關資訊」。
    內容：{context}
    問題：{input}
    """)

    document_chain = create_stuff_documents_chain(llm, prompt)
    return create_retrieval_chain(retriever, document_chain)
