import streamlit as st

# region <--------- Streamlit App Configuration --------->
st.set_page_config(
    page_title="Methodology - Hawker Guru",
    page_icon="⚙️",
    layout="wide"
)
# endregion <--------- Streamlit App Configuration --------->


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
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="big-font">Methodology</p>', unsafe_allow_html=True)
st.markdown("### Technical Implementation & Data Flow Architecture")

# Overview
st.markdown("---")
st.markdown('<p class="medium-font">System Architecture Overview</p>', unsafe_allow_html=True)
with st.container():
    st.markdown('<div class="highlight">', unsafe_allow_html=True)
    st.markdown("""
    Hawker Guru employs a modular architecture with two primary components:
    1. **Information Access System**: RAG-powered Q&A system for tender-related queries
    2. **Financial Analysis System**: Intelligent calculator for bid evaluation and planning
    
    Both systems are integrated into a unified user interface built with Streamlit, providing 
    seamless access to all features through a simple, intuitive interface.
    """)
    st.markdown('</div>', unsafe_allow_html=True)

# Use Case 1: Information Access System
st.markdown("---")
st.markdown('<p class="medium-font">Use Case 1: Information Access System</p>', unsafe_allow_html=True)

# Implementation Details
st.markdown("#### Implementation Details")
with st.container():
    st.markdown('<div class="implementation-box">', unsafe_allow_html=True)
    st.markdown("""
    **1. Data Processing Pipeline:**
    - Document ingestion and preprocessing
    - Text chunking and embedding generation
    - Vector database storage and indexing
    
    **2. Query Processing:**
    - User query vectorization
    - Semantic search in vector database
    - Context retrieval and ranking
    
    **3. Response Generation:**
    - Context-aware prompt construction
    - LLM-based response generation
    - Source attribution and verification
    """)
    st.markdown('</div>', unsafe_allow_html=True)

# Use Case 1 Flowchart
st.markdown("#### Process Flow")
try:
    st.image("placeholder_flowchart1.png", caption="Information Access System Flow", use_column_width=True)
except:
    st.markdown("""
    ```mermaid
    graph TD
        A[User Query] --> B[Query Processing]
        B --> C[Vector Search]
        C --> D[Context Retrieval]
        D --> E[Response Generation]
        E --> F[User Response]
    ```
    """)
    st.caption("Information Access System Flow (Placeholder)")

# Use Case 2: Financial Analysis System
st.markdown("---")
st.markdown('<p class="medium-font">Use Case 2: Financial Analysis System</p>', unsafe_allow_html=True)

# Implementation Details
st.markdown("#### Implementation Details")
with st.container():
    st.markdown('<div class="implementation-box">', unsafe_allow_html=True)
    st.markdown("""
    **1. Data Collection:**
    - User input gathering
    - Market data integration
    - Historical trends analysis
    
    **2. Calculation Engine:**
    - Break-even analysis
    - Cash flow projections
    - Sensitivity analysis
    
    **3. Results Processing:**
    - Risk assessment
    - Recommendation generation
    - Visualization preparation
    """)
    st.markdown('</div>', unsafe_allow_html=True)

# Use Case 2 Flowchart
st.markdown("#### Process Flow")
try:
    st.image("placeholder_flowchart2.png", caption="Financial Analysis System Flow", use_column_width=True)
except:
    st.markdown("""
    ```mermaid
    graph TD
        A[User Input] --> B[Data Processing]
        B --> C[Calculation Engine]
        C --> D[Risk Analysis]
        D --> E[Recommendations]
        E --> F[Results Display]
    ```
    """)
    st.caption("Financial Analysis System Flow (Placeholder)")

# Technical Stack
st.markdown("---")
st.markdown('<p class="medium-font">Technical Stack</p>', unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Core Technologies")
    st.markdown("""
    - **Frontend**: Streamlit
    - **Backend**: Python
    - **LLM Integration**: Claude API
    - **Vector Database**: Chroma
    - **Embedding Model**: OpenAI Ada-002
    """)

with col2:
    st.markdown("#### Key Libraries")
    st.markdown("""
    - **Data Processing**: Pandas, NumPy
    - **Text Processing**: LangChain
    - **Visualization**: Streamlit, Plotly
    - **Financial Calculations**: Custom modules
    """)

# Implementation Challenges
st.markdown("---")
st.markdown('<p class="medium-font">Implementation Considerations</p>', unsafe_allow_html=True)
with st.container():
    st.markdown("""
    **1. Data Security & Privacy**
    - Secure handling of user inputs
    - Privacy-preserving calculation methods
    - Compliance with government data policies
    
    **2. System Performance**
    - Optimization of query response times
    - Efficient vector search implementation
    - Resource usage optimization
    
    **3. Accuracy & Reliability**
    - Validation of financial calculations
    - Source verification for information
    - Regular model performance monitoring
    """)

# Note about Flowcharts
st.markdown("---")
st.info("""
**Note about Flowcharts**: The flowcharts above are placeholders. The actual flowcharts will detail:
- Step-by-step process flows
- Decision points and logic branches
- Data movement between components
- User interaction touchpoints
- System responses and outputs
""")