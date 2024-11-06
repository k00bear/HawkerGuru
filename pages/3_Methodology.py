import streamlit as st
from pathlib import Path

# Configure the page
st.set_page_config(
    page_title="Methodology - Hawker Guru",
    page_icon="⚙️",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .big-font {
        font-size:40px !important;
        font-weight:bold;
    }
    .medium-font {
        font-size:25px !important;
        font-weight:bold;
    }
    .highlight {
        padding: 20px;
        background-color: #f0f2f6;
        border-radius: 10px;
        margin: 10px 0px;
    }
    .implementation-box {
        padding: 15px;
        background-color: #e8f4ea;
        border-radius: 10px;
        margin: 10px 0px;
    }
    .tech-box {
        padding: 15px;
        background-color: #e8eaf4;
        border-radius: 10px;
        margin: 10px 0px;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="big-font">Methodology</p>', unsafe_allow_html=True)
st.markdown("### Technical Implementation & Data Flow Architecture")

# System Overview
st.markdown("---")
st.markdown('<p class="medium-font">System Architecture Overview</p>', unsafe_allow_html=True)
st.markdown("""
HawkerGuru leverages advanced AI techniques learned in ABC2024 to provide two main services:
1. **Information Access System**: An intelligent chat interface powered by RAG (Retrieval-Augmented Generation)
2. **Financial Analysis System**: A sophisticated calculator combining traditional finance with AI-driven insights
""")

# Use Case 1: Information Access System
st.markdown("---")
st.markdown('<p class="medium-font">Use Case 1: Information Access System</p>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1,3,1])
with col2:
    try:
        st.image("images/Use Case 1 Information Access System.png", 
                 caption="Information Access System Architecture", 
                 width=700) # Adjust width to control image size
    except Exception as e:
        st.error(f"Error loading image: {str(e)}")

st.markdown("#### System Components")
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="implementation-box">', unsafe_allow_html=True)
    st.markdown("""
    **1. Document Processing**
    - Ingests official documents using Document Processor
    - Implements text chunking for optimal context windows
    - Generates embeddings for semantic search
    - Stores vectors in FAISS for efficient retrieval
    """)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="implementation-box">', unsafe_allow_html=True)
    st.markdown("""
    **2. RAG Pipeline**
    - Processes user queries through semantic search
    - Retrieves relevant context from vector store
    - Assembles context for LLM processing
    - Ranks and filters results for relevance
    """)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="implementation-box">', unsafe_allow_html=True)
st.markdown("""
**3. LLM Processing**
- Implements Step-by-Step Instructions technique for structured responses
- Uses Inner Monologue approach for transparent reasoning
- Employs custom prompt templates for consistent outputs
- Leverages OpenAI LLM for natural language generation
""")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("#### ABC2024 Techniques Implementation")
st.markdown('<div class="tech-box">', unsafe_allow_html=True)
st.markdown("""
The Information Access System integrates several key techniques from ABC2024:

1. **Linear Chain Processing**
   - Sequential document processing workflow
   - Structured content transformation
   - Systematic context building

2. **Decision Chain Implementation**
   - Smart context selection
   - Adaptive response generation
   - Dynamic content filtering

3. **Step-by-Step & Inner Monologue**
   - Transparent reasoning process
   - Clear explanation structure
   - Validated response generation
""")
st.markdown('</div>', unsafe_allow_html=True)

# Use Case 2: Financial Analysis System
st.markdown("---")
st.markdown('<p class="medium-font">Use Case 2: Financial Analysis System</p>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1,3,1])
with col2:
    try:
        st.image("images/Use Case 2 Financial Analysis System.png", 
                 caption="Financial Analysis System Architecture", 
                 width=800) # Adjust width to control image size
    except Exception as e:
        st.error(f"Error loading image: {str(e)}")

st.markdown("#### System Components")
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="implementation-box">', unsafe_allow_html=True)
    st.markdown("""
    **1. Input Processing**
    - Validates user inputs for completeness
    - Processes revenue parameters
    - Handles cost parameters
    - Manages operating parameters
    """)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="implementation-box">', unsafe_allow_html=True)
    st.markdown("""
    **2. Calculation Engine**
    - Performs financial calculations
    - Conducts break-even analysis
    - Determines sustainable bid ranges
    - Generates financial projections
    """)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="implementation-box">', unsafe_allow_html=True)
st.markdown("""
**3. LLM Analysis**
- Conducts step-by-step business review
- Performs inner monologue analysis
- Generates contextual recommendations
- Provides actionable insights
""")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("#### ABC2024 Techniques Implementation")
st.markdown('<div class="tech-box">', unsafe_allow_html=True)
st.markdown("""
The Financial Analysis System leverages these ABC2024 techniques:

1. **Linear Chain for Input Processing**
   - Sequential validation
   - Structured data transformation
   - Systematic parameter processing

2. **Decision Chain for Analysis**
   - Adaptive bid range determination
   - Dynamic risk assessment
   - Contextual recommendation generation

3. **Step-by-Step Review Process**
   - Systematic business analysis
   - Transparent financial assessment
   - Clear recommendation structure
""")
st.markdown('</div>', unsafe_allow_html=True)

# Technical Integration
st.markdown("---")
st.markdown('<p class="medium-font">Technical Integration</p>', unsafe_allow_html=True)
st.markdown('<div class="highlight">', unsafe_allow_html=True)
st.markdown("""
The system integrates various technologies to deliver its functionality:

**Core Components:**
- Streamlit for the user interface
- FAISS for vector storage and retrieval
- OpenAI API for LLM capabilities
- Custom Python modules for financial calculations

**Key Libraries:**
- LangChain for RAG implementation
- Pandas for data processing
- NumPy for numerical computations
- Custom modules for document processing
""")
st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.caption("Made with ❤️ by koobear | ABC2024 Graduation Project | © 2024")