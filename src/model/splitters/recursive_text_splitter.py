"""
This document is responsible to return a splitter that uses Recursive Text Strategy
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter


def return_basic_text_splitter():
    """
    This funct is responsible for returning a recursive character text splitter with some default arguments
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200, add_start_index=True
    )

    return text_splitter
