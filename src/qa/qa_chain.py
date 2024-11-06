from typing import List, Dict
from datetime import datetime
import logging
from pathlib import Path

import streamlit as st
from langchain.chains import ConversationalRetrievalChain
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain.docstore.document import Document

from src.data_processing.managers.document_manager import DocumentManager

logger = logging.getLogger(__name__)

def get_doc_score(doc: Document, query: str) -> float:
    """Calculate document relevance score."""
    base_score = 1.0
    
    # Prioritize documents based on type
    doc_type = doc.metadata.get('type', '').lower()
    type_weights = {
        'faq': 1.3,  # FAQ gets 30% boost - most direct answers
        'terms_and_conditions': 1.2,  # T&C gets 20% boost - authoritative source
        'tender_notice': 1.1,  # Notice gets 10% boost - current information
        'general': 1.0  # Base weight for other documents
    }
    type_weight = type_weights.get(doc_type, 1.0)
    
    # Boost recent documents
    doc_date = doc.metadata.get('date')
    if doc_date:
        try:
            date_obj = datetime.strptime(doc_date, '%b %Y')
            days_old = (datetime.now() - date_obj).days
            recency_weight = 1.0 if days_old <= 30 else 0.9
        except ValueError:
            recency_weight = 1.0
    else:
        recency_weight = 1.0
    
    # Apply query-specific boosting
    query_lower = query.lower()
    
    # Boost FAQ for how-to and what-is questions
    if doc_type == 'faq' and any(term in query_lower for term in 
        ['how', 'what', 'when', 'where', 'who', 'why', 'can i', 'do i']):
        base_score *= 1.2
        
    # Boost T&C for rule and requirement questions
    elif doc_type == 'terms_and_conditions' and any(term in query_lower for term in 
        ['rule', 'requirement', 'must', 'legal', 'condition', 'term']):
        base_score *= 1.2
        
    # Boost Tender Notice for current tender questions
    elif doc_type == 'tender_notice' and any(term in query_lower for term in 
        ['current', 'latest', 'tender', 'date', 'deadline']):
        base_score *= 1.2
    
    return base_score * type_weight * recency_weight

def get_qa_prompt() -> PromptTemplate:
    """Get the custom prompt template for QA."""
    template = """You are HawkerGuru, an expert assistant for Singapore hawker stall bidding. Use the following context to answer the question at the end.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    Use the following guidelines when answering:
    
    1. If the question is about rules or requirements:
       - First cite the official Terms & Conditions
       - Then reference any FAQ or Notice clarifications
       - Explain in simple terms
    
    2. If the question is about processes or procedures:
       - Start with the FAQ explanation if available
       - Add details from other documents if relevant
       - Give step-by-step guidance
    
    3. If the question is about current tenders:
       - Prioritize information from the current Tender Notice
       - Add context from T&C if needed
       - Note any special conditions
    
    4. For any answer:
       - Be clear and concise
       - Cite sources when quoting rules
       - Offer to explain further if needed
    
    Context: {context}
    
    Chat History: {chat_history}
    
    Question: {question}
    
    Helpful Answer:"""
    
    return PromptTemplate(
        template=template,
        input_variables=["context", "chat_history", "question"]
    )

def setup_qa_chain(documents: List[Document]) -> ConversationalRetrievalChain:
    """Setup QA chain with enhanced document prioritization and retrieval."""
    logger.info("Setting up QA chain...")
    
    # Create embeddings with better parameters
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        embedding_ctx_length=8191,  # Maximum context length
        chunk_size=1000  # Process in larger chunks
    )
    
    # Create vector store with custom scoring
    vectorstore = FAISS.from_documents(
        documents,
        embeddings,
        relevance_score_fn=get_doc_score
    )
    
    # Configure retriever with better parameters
    retriever = vectorstore.as_retriever(
        search_kwargs={
            "k": 6,  # Retrieve top 6 chunks
            "score_threshold": 0.7,  # Minimum relevance score
            "fetch_k": 10  # Fetch more candidates for reranking
        }
    )
    
    # Create QA chain with custom configuration
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=ChatOpenAI(
            temperature=0,
            model_name="gpt-4o-mini",
            max_tokens=2048
        ),
        retriever=retriever,
        return_source_documents=True,
        combine_docs_chain_kwargs={"prompt": get_qa_prompt()},
        verbose=True
    )
    
    logger.info("QA chain setup complete")
    return qa_chain

@st.cache_resource
def setup_hawker_guru() -> ConversationalRetrievalChain:
    """Setup the Hawker Guru chatbot with document manager integration."""
    logger.info("Setting up Hawker Guru...")
    
    # Initialize document manager
    doc_manager = DocumentManager(Path("data"))
    
    # Load all current documents
    documents = []
    for doc_type in ['faq', 'tender_notice', 'terms_and_conditions']:
        current_file = doc_manager.get_current_file(doc_type)
        if current_file and current_file.exists():
            try:
                with open(current_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    documents.append(Document(
                        page_content=content,
                        metadata={
                            "source": doc_type,
                            "type": doc_type,
                            "date": "Aug 2024"
                        }
                    ))
                logger.info(f"Loaded {doc_type} document")
            except Exception as e:
                logger.error(f"Error loading {doc_type}: {str(e)}")
    
    # Create QA chain
    qa_chain = setup_qa_chain(documents)
    
    logger.info("Hawker Guru setup complete!")
    return qa_chain