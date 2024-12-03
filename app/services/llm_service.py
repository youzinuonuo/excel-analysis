from pandasai import Agent
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from typing import List, Dict
from app.services.file_service import FileService
import os

class LLMService:
    def __init__(self, file_service: FileService):
        self.file_service = file_service
        self.agents = {}  # 使用字典存储不同会话的agent
        self.dataframes = {}  # 使用字典存储不同会话的dataframes

    async def initialize_chat(self, session_id: str, file_info: Dict[str, str], api_key: str):
        """初始化Agent和数据框"""
        try:
            # 解析Excel文件并保存到实例变量
            self.dataframes[session_id] = self.file_service.parse_excel_files(file_info)
            
            if not self.dataframes[session_id]:
                raise Exception("没有有效的数据文件")
            
            # 设置API密钥
            os.environ["PANDASAI_API_KEY"] = api_key
            
            # 初始化Agent，传入所有数据框列表
            dataframes_list = []
            for name, df in self.dataframes[session_id].items():
                df.name = name
                # 将 NaN 值替换为 None
                df = df.replace({pd.NA: None, pd.NaT: None, float('nan'): None})
                dataframes_list.append(df)
            
            self.agents[session_id] = Agent(dataframes_list, memory_size=10)
            
            # 返回数据框信息，处理 NaN 值
            return {
                "session_id": session_id,
                "dataframes": {
                    name: df.fillna("").head().to_dict() 
                    for name, df in self.dataframes[session_id].items()
                }
            }
            
        except Exception as e:
            raise Exception(f"初始化对话失败: {str(e)}")

    async def chat(self, session_id: str, query: str):
        """与Agent对话"""
        if session_id not in self.agents:
            raise Exception("会话未初始化，请先上传文件")
            
        try:
            response = self.agents[session_id].chat(query)
            print(f"Agent响应类型: {type(response)}")
            print(f"Agent响应内容: {response}")
            
            if isinstance(response, str):
                return {"text": response}
            else:
                return {"chart_data": self._convert_plot_to_base64(response)}
                
        except Exception as e:
            raise Exception(f"对话失败: {str(e)}")

    def _convert_plot_to_base64(self, fig) -> str:
        """将图表转换为base64字符串"""
        buffer = io.BytesIO()
        if hasattr(fig, 'figure'):
            fig.figure.savefig(buffer, format='png')
        else:
            fig.savefig(buffer, format='png')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close(fig)
        return image_base64 