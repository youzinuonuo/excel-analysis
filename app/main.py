from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from app.services.llm_service import LLMService
from app.services.file_service import FileService
from pydantic import BaseModel

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

class AnalyzeRequest(BaseModel):
    query: str
    api_key: str
    use_pandas_ai: bool = True

@app.post("/api/analyze")
async def analyze_files(
    files: List[UploadFile] = File(...),
    query: str = None,
    api_key: str = None,
    use_pandas_ai: bool = True
):
    """
    分析上传的文件并生成图表
    """
    try:
        # 使用 file_service 保存文件
        file_paths = await file_service.save_uploaded_files(files)
        
        try:
            # 调用LLM服务生成图表
            chart_data = await llm_service.generate_chart(
                file_paths, 
                query, 
                api_key, 
                use_pandas_ai
            )
            return {"chart_data": chart_data}
        finally:
            # 使用 file_service 清理文件
            await file_service.cleanup_files(file_paths)
                    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 健康检查接口
@app.get("/health")
async def health_check():
    return {"status": "healthy"} 