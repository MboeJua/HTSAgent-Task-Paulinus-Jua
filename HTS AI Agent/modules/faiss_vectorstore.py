import os
import warnings
from langchain.prompts import PromptTemplate
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from transformers import AutoTokenizer, pipeline ,AutoModelForSeq2SeqLM
from langchain_huggingface import HuggingFacePipeline
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferMemory
import numpy as np
import pandas as pd
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType
from langchain.agents import Tool, initialize_agent, AgentType
import pandas as pd
import re
from tariff_cal import *

warnings.filterwarnings(action="ignore")

pdf_path = os.path.join(os.path.dirname(__file__), 'tariff_agent_data\\General Notes.pdf')

loader = PyPDFLoader(pdf_path)
data = loader.load()

splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=50)
chunks = splitter.split_documents(data)

embedder = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-mpnet-base-v2",
    model_kwargs={"device": "cpu"} 
)


vectorstore = FAISS.from_documents(
    documents=chunks,
    embedding=embedder
)
retriever = vectorstore.as_retriever()

vectorstore.save_local("faiss_index")
