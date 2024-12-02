import pandas as pd
import matplotlib.pyplot as plt
import base64
from io import BytesIO

class ChartService:
    async def generate_chart(self, chart_code: str, file_paths: list):
        """
        执行生成的代码并返回图表数据
        """
        # 创建本地变量环境
        local_vars = {
            'pd': pd,
            'plt': plt,
            'files': file_paths
        }
        
        # 执行代码
        exec(chart_code, globals(), local_vars)
        
        # 获取图表数据
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        
        # 转换为base64
        graphic = base64.b64encode(image_png).decode()
        
        return graphic 