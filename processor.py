import os
from typing import List, Dict
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_community.document_loaders import TextLoader, UnstructuredWordDocumentLoader
from langchain.docstore.document import Document
import json
import streamlit as st

load_dotenv()

@st.cache_data
def load_documents(data_dir: str = "Data") -> List[Document]:
    """
    Load all documents from the data directory
    """
    documents = []
    print("\nStarting document loading process...")

    # First, create AOS reference document
    json_path = os.path.join(data_dir, "article_of_sale.json")
    if os.path.exists(json_path):
        print(f"Loading AOS data from: {json_path}")
        with open(json_path, 'r', encoding='utf-8') as f:
            articles = json.load(f)
            print(f"Found {len(articles)} articles of sale")
            
            # Create general AOS reference document
            aos_content = "General Guide to Articles of Sale:\n\n"
            
            # Group by Trade Type Category for better organization
            categories = {}
            for article in articles:
                category = article['Trade Type Category']
                if category not in categories:
                    categories[category] = []
                categories[category].append(article)
            
            # Create structured content for each category
            for category, items in categories.items():
                aos_content += f"\nTrade Type Category: {category}\n"
                for item in items:
                    aos_content += f"Stall Type: {item['Stall Type']}\n"
                    aos_content += f"Article of Sale: {item['Article of Sale']}\n"
                    if item['Remarks']:
                        aos_content += f"Special Notes: {item['Remarks']}\n"
                    aos_content += "\n"
            
            # Add as a document
            documents.append(Document(
                page_content=aos_content,
                metadata={"source": "article_of_sale.json", "type": "reference_guide"}
            ))
            print("Created AOS reference guide document")

    # Load Word document for tender notice and restrictions
    word_path = os.path.join(data_dir, "Aug 2024 Tender Notice_Text Only.docx")
    if os.path.exists(word_path):
        print(f"Loading tender notice from: {word_path}")
        loader = UnstructuredWordDocumentLoader(word_path)
        tender_docs = loader.load()
        
        # Add metadata to identify this as location-specific rules
        for doc in tender_docs:
            doc.metadata["type"] = "location_rules"
            documents.append(doc)
        print(f"Loaded tender notice with restrictions")

    # Load other text files
    text_files = [
        "ThingsToNoteWhenTendering.txt",
    ]
    
    for file in text_files:
        file_path = os.path.join(data_dir, file)
        if os.path.exists(file_path):
            print(f"Loading text file: {file}")
            loader = TextLoader(file_path)
            loaded_docs = loader.load()
            for doc in loaded_docs:
                doc.metadata["type"] = "general_info"
                documents.append(doc)
            print(f"Loaded {file}")

    print(f"\nTotal documents loaded: {len(documents)}")
    return documents

@st.cache_resource
def create_vector_store(_documents):
    """
    Create and cache the vector store
    """
    print("\nCreating vector store...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=200,
        length_function=len
    )
    texts = text_splitter.split_documents(_documents)
    print(f"Split into {len(texts)} text chunks")
    
    embeddings = OpenAIEmbeddings()
    return FAISS.from_documents(texts, embeddings)

@st.cache_resource
def setup_hawker_guru():
    """
    Setup the Hawker Guru chatbot
    """
    print("\nSetting up Hawker Guru...")
    
    # Load documents
    documents = load_documents()
    
    # Create vector store
    vectorstore = create_vector_store(documents)
    
    # Create chat model
    llm = ChatOpenAI(
        temperature=0,
        model_name="gpt-4o-mini"
    )
    
    # Create conversational chain
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(
            search_kwargs={"k": 6}  # Increased to get more context
        ),
        return_source_documents=True,
        verbose=True
    )
    
    return qa_chain