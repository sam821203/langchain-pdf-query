from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from pdf_processing import load_and_create_vector_store
from query_chain import create_query_chain
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
import uuid

# 初始化 FastAPI 應用
app = FastAPI()

# 設定 CORS 規則
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 定義請求和回應格式
class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str

class PDFUpdateRequest(BaseModel):
    pdf_path: str

# 設定儲存 PDF 的暫存資料夾
UPLOAD_FOLDER = "./uploaded_pdfs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

vectorstores = None
query_chain = None
current_pdf_path = None

def initialize_pdf(pdf_path):
    """Initialize or reinitialize the PDF processing chain"""
    # global vectorstores, query_chain
    global vectorstores, query_chain, current_pdf_path
    current_pdf_path = pdf_path
    vectorstores = load_and_create_vector_store(current_pdf_path)
    query_chain = create_query_chain(vectorstores)

@app.post("/upload-pdf", response_model=dict)
async def upload_pdf(file: UploadFile = File(...)):
    """
    接收 PDF 檔案並初始化查詢鏈
    """
    try:
        # 生成唯一的檔名，避免檔案名稱衝突
        print("收到的檔案：", file.filename)
        file_ext = file.filename.split(".")[-1].lower()
        if file_ext != "pdf":
            raise HTTPException(status_code=400, detail="僅支援 PDF 檔案")

        file_id = str(uuid.uuid4())  # 生成唯一 ID
        file_path = os.path.join(UPLOAD_FOLDER, f"{file_id}.pdf")
        print('檔案：', file_path)
        # 儲存檔案
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 初始化查詢鏈
        initialize_pdf(file_path)
        return {"message": "PDF 上傳並初始化成功", "pdf_path": file_path}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上傳 PDF 時發生錯誤：{str(e)}")

# 查詢 API：根據使用者問題從上傳的 PDF 中檢索答案
@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    try:
        if query_chain is None:
            raise HTTPException(status_code=400, detail="尚未上傳 PDF")

        response = query_chain.invoke({"input": request.question})
        return QueryResponse(answer=response["answer"])
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查詢錯誤：{str(e)}")
    
# 設定根端點
@app.get("/")
async def root():
    return {"message": "歡迎來到PDF內容查詢系統！請上傳 PDF 來開始分析。"}