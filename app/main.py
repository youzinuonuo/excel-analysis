from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
from app.services.llm_service import LLMService
from app.services.file_service import FileService
from pydantic import BaseModel
import uuid

app = FastAPI()

# CORS设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化服务
file_service = FileService()
llm_service = LLMService(file_service)

# 会话存储
sessions: Dict[str, List[str]] = {}

class AnalyzeRequest(BaseModel):
    query: str
    api_key: str
    use_pandas_ai: bool = True

@app.post("/api/start-analysis")
async def start_analysis(
    files: List[UploadFile] = File(...),
    table_names: List[str] = Form(...),
    api_key: str = Form(...)
):
    """开始分析并初始化Agent"""
    try:
        # 保存文件并获取文件信息
        file_info = await file_service.save_uploaded_files(files, table_names)
        
        # 创建会话ID
        session_id = str(uuid.uuid4())
        sessions[session_id] = {
            "file_info": file_info,
            "api_key": api_key
        }
        
        # 初始化对话，传入session_id
        result = await llm_service.initialize_chat(session_id, file_info, api_key)
        return result  # result已包含session_id
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/query")
async def analyze_query(
    session_id: str,
    query: str
):
    """查询Agent"""
    try:
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="会话ID未找到")
        
        # 直接调用chat方法获取响应
        response = await llm_service.chat(query)
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 健康检查接口
@app.get("/health")
async def health_check():
    return {"status": "healthy"} 