from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_community.retrievers import BM25Retriever
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

def load_and_create_vector_store(pdf_path):
    global vectorstores  

    # #region agent log
    try:
        _log_dir = "/Users/huangyuhao/pdf-query-app/.cursor"
        os.makedirs(_log_dir, exist_ok=True)
        open(os.path.join(_log_dir, "debug.log"), "a").write(
            __import__("json").dumps({"id": "log_load_entry", "timestamp": __import__("time").time() * 1000, "location": "pdf_processing.py:load_and_create_vector_store", "message": "load_and_create_vector_store entry", "data": {"pdf_path": pdf_path}, "hypothesisId": "A,C"}) + "\n"
        )
    except Exception:
        pass
    # #endregion

    os.makedirs(VECTOR_DB_PATH, exist_ok=True)

    try:
        clear_vector_store()

        vectorstores = None

        # 建立新的嵌入向量
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        
        # 解析 PDF
        loader = PyPDFLoader(pdf_path)
        pages = loader.load_and_split()

        # 建立新的 Chroma 向量資料庫
        vectorstores = Chroma.from_documents(
            documents=pages,
            embedding=embeddings,
            persist_directory=VECTOR_DB_PATH
        )

        # 建立 BM25 檢索器（同一份 pages，供 hybrid search 使用）
        bm25_retriever = BM25Retriever.from_documents(pages)
        bm25_retriever.k = 2

        # #region agent log
        try:
            os.makedirs("/Users/huangyuhao/pdf-query-app/.cursor", exist_ok=True)
            open("/Users/huangyuhao/pdf-query-app/.cursor/debug.log", "a").write(
                __import__("json").dumps({"id": "log_load_ok", "timestamp": __import__("time").time() * 1000, "location": "pdf_processing.py:load_and_create_vector_store", "message": "load_and_create_vector_store success", "data": {"vectorstores_is_none": vectorstores is None}, "hypothesisId": "A"}) + "\n"
            )
        except Exception:
            pass
        # #endregion

        return (vectorstores, bm25_retriever)
    except Exception as e:
        # #region agent log
        try:
            os.makedirs("/Users/huangyuhao/pdf-query-app/.cursor", exist_ok=True)
            open("/Users/huangyuhao/pdf-query-app/.cursor/debug.log", "a").write(
                __import__("json").dumps({"id": "log_load_ex", "timestamp": __import__("time").time() * 1000, "location": "pdf_processing.py:load_and_create_vector_store", "message": "load_and_create_vector_store exception", "data": {"type": type(e).__name__, "str_e": str(e), "repr_e": repr(e)}, "hypothesisId": "A,C"}) + "\n"
            )
        except Exception:
            pass
        # #endregion
        return (None, None)
