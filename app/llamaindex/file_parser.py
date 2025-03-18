import os
from typing import Union, List
from xml.dom.minidom import Document

from llama_index.readers.dashscope.base import DashScopeParse
from llama_index.readers.dashscope.utils import ResultType
from llama_index.core import SimpleDirectoryReader

# 多个独立文件
def parse_file(file_paths: Union[List[str], str]) -> List[Document]:
    parse = DashScopeParse(result_type=ResultType.DASHSCOPE_DOCMIND)
    documents = parse.load_data(file_path=file_paths)
    return documents

'''
    ".hwp": HWPReader,
    ".pdf": PDFReader,
    ".docx": DocxReader,
    ".pptx": PptxReader,
    ".ppt": PptxReader,
    ".pptm": PptxReader,
    ".gif": ImageReader,
    ".jpg": ImageReader,
    ".png": ImageReader,
    ".jpeg": ImageReader,
    ".webp": ImageReader,
    ".mp3": VideoAudioReader,
    ".mp4": VideoAudioReader,
    ".csv": PandasCSVReader,
    ".epub": EpubReader,
    ".mbox": MboxReader,
    ".ipynb": IPYNBReader,
    ".xls": PandasExcelReader,
    ".xlsx": PandasExcelReader,
'''
# 使用SimpleDirectoryReader读取文件夹下所有文件

def parse_directory(directory_path: str) -> List[Document]:
    parse = DashScopeParse(result_type=ResultType.DASHSCOPE_DOCMIND)
    documents = SimpleDirectoryReader(
        directory_path,
    ).load_data(num_workers=1)
    return documents