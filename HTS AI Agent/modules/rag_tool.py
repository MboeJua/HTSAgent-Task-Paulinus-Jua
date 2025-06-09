from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from transformers import AutoTokenizer, pipeline ,AutoModelForSeq2SeqLM
from langchain_huggingface import HuggingFacePipeline
import os
import warnings
warnings.filterwarnings('ignore')


path = os.path.join(os.path.dirname(__file__), 'faiss_index')

embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
retriever = FAISS.load_local(folder_path=path, embeddings=embedding,allow_dangerous_deserialization=True).as_retriever()

tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-base")
model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-base", device_map="cpu")

pipe = pipeline("text2text-generation", model=model, tokenizer=tokenizer,
                max_new_tokens=512,truncation=True
                )
llm = HuggingFacePipeline(pipeline=pipe)


system_template = ("You are TariffBot — an intelligent assistant trained on U.S. International Trade Commission data."
"You exist to help importers, analysts, and trade professionals quickly understand tariff rules, duty rates, and policy agreements."
" You always provide clear, compliant, and factual answers grounded in official HTS documentation."
"When given an HTS code and product information, you explain all applicable duties and cost components."
"When asked about trade agreements (e.g., NAFTA, Israel FTA), you reference the relevant General Notes with citations."
"If a query is ambiguous or unsupported, you politely defer or recommend reviewing the relevant HTS section manually."
"You do not speculate or make policy interpretations — you clarify with precision and data.")


condense_question_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_template),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
    ]
)

history_aware_retriever = create_history_aware_retriever(
    llm, retriever, condense_question_prompt
)

system_prompt = (
    "You are an assistant for question-answering tasks. "
    "Use the following pieces of retrieved context to answer "
    "the question. If you don't know the answer, say that you "
    "don't know. Use three sentences maximum and keep the "
    "answer concise."
    "\n\n"
    "{context}"
)

qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
    ]
)

llm_chain = create_stuff_documents_chain(llm=llm, prompt=qa_prompt)

rag_chain = create_retrieval_chain(history_aware_retriever, llm_chain)

def rag_tool_func(input_question: str, chat_history: list = None) -> str:
    messages = []
    if chat_history:
        for q, a in chat_history:
            messages.append(("human", q))
            messages.append(("ai", a))

    result = rag_chain.invoke({
        "input": input_question,
        "chat_history": messages  
    })
    return result["answer"]

