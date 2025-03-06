from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
import os
import time

VECTOR_DB_PATH = "./vector"
vectorstores = None

def clear_vector_store():
    # 清除 Chroma 向量索引，但不刪除資料夾
    global vectorstores

    # 確保 vectorstores 不再使用
    if vectorstores:
        # 釋放 Chroma 物件，確保不會連接舊的 DB
        del vectorstores  
        vectorstores = None
        time.sleep(1)

    # 只刪除索引檔案，而不刪除整個目錄
    files_to_remove = [
        os.path.join(VECTOR_DB_PATH, "chroma-collections.parquet"),
        os.path.join(VECTOR_DB_PATH, "chroma-embeddings.parquet")
    ]
    for file in files_to_remove:
        if os.path.exists(file):
            os.remove(file)
    
    print("Chroma 向量索引已清除")

def load_and_create_vector_store(pdf_path):
    global vectorstores  

    os.makedirs(VECTOR_DB_PATH, exist_ok=True)

    try:
        clear_vector_store()

        vectorstores = None

        # 建立新的嵌入向量
        embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
        
        # 解析 PDF
        loader = PyPDFLoader(pdf_path)
        pages = loader.load_and_split()

        # 建立新的 Chroma 向量資料庫
        vectorstores = Chroma.from_documents(
            documents=pages,
            embedding=embeddings,
            persist_directory=VECTOR_DB_PATH
        )

        return vectorstores
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
