# LangChain PDF 加載、向量資料庫建立邏輯
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
import os

def load_and_create_vector_store(pdf_path):
    embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
    loader = PyPDFLoader(pdf_path)
    pages = loader.load_and_split()
    
    vectorstore = Chroma.from_documents(
        documents=pages,
        embedding=embeddings,
        persist_directory="./vector"
    )
    vectorstore.persist()
    return vectorstore
