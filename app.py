from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import TextLoader
from langchain.memory import ConversationBufferMemory
import dotenv
import openai
import pandas as pd
import requests
import os

app = Flask(__name__)
CORS(app)

# load api key
dotenv.load_dotenv()

@app.route('/ask_openai', methods=['POST'])
def ask_openai():
    # Load all .txt files from the input folder
    documents = []
    files = os.listdir("input")
    for file_name in files:
        if file_name.endswith(".txt"):
            loader = TextLoader("input/" + file_name)
            loaded = loader.load()
            for item in loaded:
                documents.append(item)

    # Split the input
    text_splitter = CharacterTextSplitter(chunk_size=15000, chunk_overlap=500)
    texts = text_splitter.split_documents(documents)

    # Create the vector storage
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(texts, embeddings)

    # Create the conversation memory
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    # Setup the prompt template
    system_template = """Use the following pieces of context to answer the user's question. Only use the supplied context to answer.
    If you cannot find the answer from the pieces of context, just say that you don't know, don't try to make up an answer.
    ----------------
    {context}"""
    messages = [
        SystemMessagePromptTemplate.from_template(system_template),
        HumanMessagePromptTemplate.from_template("{question}")
    ]
    qa_prompt = ChatPromptTemplate.from_messages(messages)

    # Create the question and answer conversation chain
    qa = ConversationalRetrievalChain.from_llm(ChatOpenAI(model_name="gpt-3.5-turbo-16k", temperature=0), vectorstore.as_retriever(search_kwargs={"k": 4}), combine_docs_chain_kwargs={"prompt": qa_prompt}, memory=memory)

    data = request.get_json()
    query = data['query']
    result = qa.invoke({"question": query})
    return jsonify({'answer': result['answer']})

if __name__ == '__main__':
    app.run(debug=True)
