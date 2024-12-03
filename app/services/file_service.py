from pathlib import Path
import pandas as pd
from typing import List, Dict
import os

class FileService:
    def __init__(self):
        self.upload_dir = Path("uploads")
        self.upload_dir.mkdir(exist_ok=True)
    
    async def save_uploaded_files(self, files: List[dict], table_names: List[str]) -> Dict[str, str]:
        """保存上传的文件并返回文件路径和表名的映射"""
        file_info = {}
        for file, table_name in zip(files, table_names):
            file_path = self.upload_dir / file.filename
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            # 如果没有提供表名，使用文件名（不包含扩展名）
            actual_table_name = table_name if table_name else Path(file.filename).stem
            file_info[str(file_path)] = actual_table_name
        return file_info
    
    def parse_excel_files(self, file_info: Dict[str, str]) -> Dict[str, pd.DataFrame]:
        """解析Excel文件并返回DataFrame字典,使用指定的表名"""
        dataframes = {}
        for file_path, table_name in file_info.items():
            try:
                if file_path.endswith(('.xlsx', '.xls')):
                    df = pd.read_excel(file_path)
                elif file_path.endswith('.csv'):
                    df = pd.read_csv(file_path)
                else:
                    continue
                dataframes[table_name] = df
            except Exception as e:
                print(f"解析文件 {file_path} 时出错: {str(e)}")
        return dataframes
    
    def cleanup_files(self, file_paths: List[str]):
        """清理上传的文件"""
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"删除文件 {file_path} 时出错: {str(e)}") 