"""
This file is responsible to return a basic web loader
"""

import bs4
from langchain_community.document_loaders import WebBaseLoader


def return_basic_web_loader():
    bs4_strainer = bs4.SoupStrainer(class_=("Table"))

    loader = WebBaseLoader(
        web_paths=("https://brasilescola.uol.com.br/biologia/conceitos-botanicos.htm",),
        bs_kwargs={"parse_only": bs4_strainer},
    )

    return loader

    # docs = loader.load()
