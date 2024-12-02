from pandasai import SmartDataframe
from pandasai.llm import OpenAI
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from typing import List
from fastapi import UploadFile
from app.services.file_service import FileService

class LLMService:
    def __init__(self, file_service: FileService):
        self.smart_df = None
        self.file_service = file_service

    async def generate_chart(self, file_paths: List[str], query: str, api_key: str, use_pandas_ai: bool = True):
        """生成图表"""
        try:
            # 解析Excel文件
            dataframes = self.file_service.parse_excel_files(file_paths)
            
            if not dataframes:
                raise Exception("没有有效的数据文件")
            
            # 合并所有数据框
            final_df = pd.concat(dataframes.values(), axis=1)
            
            try:
                if use_pandas_ai:
                    # PandasAI模式
                    llm = OpenAI(api_token=api_key)
                    self.smart_df = SmartDataframe(final_df, config={"llm": llm})
                    fig = self.smart_df.chat(f"基于提供的数据，{query}")
                    return self._convert_plot_to_base64(fig)
                else:
                    # 普通LLM模式
                    code = await self._generate_chart_code_from_llm(query, api_key)
                    local_vars = {'df': final_df, 'plt': plt}
                    exec(code, globals(), local_vars)
                    fig = plt.gcf()
                    return self._convert_plot_to_base64(fig)
                    
            except Exception as e:
                raise Exception(f"生成图表失败: {str(e)}")
                
        except Exception as e:
            raise Exception(f"处理数据失败: {str(e)}")

    def _convert_plot_to_base64(self, fig) -> str:
        """将图表转换为base64字符串"""
        buffer = io.BytesIO()
        if hasattr(fig, 'figure'):  # 如果是PandasAI返回的图表对象
            fig.figure.savefig(buffer, format='png')
        else:  # 如果是matplotlib的Figure对象
            fig.savefig(buffer, format='png')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close(fig)  # 清理图表资源
        return image_base64

    async def _generate_chart_code_from_llm(self, query: str, api_key: str) -> str:
        """从其他LLM获取图表代码"""
        # 这里需要实现与其他LLM的集成
        # 示例prompt
        prompt = f"""
        基于以下需求生成Python代码:{query}
        要求：
        1. 使用matplotlib或seaborn库
        2. 假设数据在变量df中
        3. 只返回Python代码, 不要包含任何解释
        4. 确保代码完整可运行
        5. 包含适当的标题、标签和图例
        """
        # TODO: 实现与其他LLM的集成
        # 临时返回一个示例代码
        return """
import matplotlib.pyplot as plt
import seaborn as sns

plt.figure(figsize=(10, 6))
sns.lineplot(data=df)
plt.title('数据可视化')
plt.xlabel('索引')
plt.ylabel('值')
plt.grid(True)
""" 