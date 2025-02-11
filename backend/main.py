from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pdf_processing import load_and_create_vector_store
from query_chain import create_query_chain
from fastapi.middleware.cors import CORSMiddleware

# 初始化 FastAPI 應用
app = FastAPI()

# 設定 CORS 規則
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允許所有來源（開發環境使用，正式環境應設定特定 domain）
    allow_credentials=True,
    allow_methods=["*"],  # 允許所有 HTTP 方法
    allow_headers=["*"],  # 允許所有 Headers
)

# 定義請求和回應格式
class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str

# 載入 PDF 並創建查詢鏈
pdf_path = "./path_to_pdf/鳥類/繫放.pdf"  # PDF 檔案的路徑
vectorstore = load_and_create_vector_store(pdf_path)
query_chain = create_query_chain(vectorstore)

@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    查詢 API：接收問題並返回從 PDF 文件中檢索到的答案
    """
    print('............', request)
    try:
        # 使用 LangChain 查詢鏈來處理問題
        response = query_chain.invoke({
            "input": request.question
        })

        # 回傳查詢結果
        return QueryResponse(answer=response["answer"])
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查詢錯誤：{str(e)}")

# 設定根端點
@app.get("/")
async def root():
    return {"message": "歡迎來到鳥類資訊查詢系統！"}