import streamlit as st

# region <--------- Streamlit App Configuration --------->
st.set_page_config(
    page_title="Source Code - Hawker Guru",
    page_icon="👨‍💻",
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
    .code-box {
        padding: 15px;
        background-color: #f8f9fa;
        border-radius: 10px;
        margin: 10px 0px;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="big-font">Source Code</p>', unsafe_allow_html=True)
st.markdown("### Project Documentation & Code Repository")

# GitHub Repository
st.markdown("---")
st.markdown('<p class="medium-font">GitHub Repository</p>', unsafe_allow_html=True)
with st.container():
    st.markdown('<div class="highlight">', unsafe_allow_html=True)
    # Replace with your actual GitHub repository URL
    github_url = "https://github.com/yourusername/hawker-guru"
    st.markdown(f"""
    The complete source code for Hawker Guru is available on GitHub:
    - Repository URL: [{github_url}]({github_url})
    - License: MIT License
    - Last Updated: October 2024
    """)
    st.markdown('</div>', unsafe_allow_html=True)

# Project Structure
st.markdown("---")
st.markdown('<p class="medium-font">Project Structure</p>', unsafe_allow_html=True)
with st.container():
    st.markdown('<div class="code-box">', unsafe_allow_html=True)
    st.code("""
HawkerGuru/
├── app.py                      # Main application file
├── requirements.txt            # Project dependencies
├── README.md                   # Project documentation
├── .gitignore                 # Git ignore file
├── pages/                     # Streamlit pages
│   ├── 2_About_Us.py          # About page
│   ├── 3_Methodology.py       # Methodology page
│   └── 4_Source_Code.py       # This page
├── components/                # Custom components
│   ├── qa_system.py          # Q&A system implementation
│   └── financial_calc.py     # Financial calculator implementation
├── utils/                    # Utility functions
│   ├── data_processing.py    # Data processing utilities
│   └── prompts.py           # LLM prompt templates
├── data/                     # Data files
│   ├── processed/           # Processed data
│   └── raw/                 # Raw data
└── tests/                   # Unit tests
    └── test_components.py   # Component tests
""")
    st.markdown('</div>', unsafe_allow_html=True)

# Key Components
st.markdown("---")
st.markdown('<p class="medium-font">Key Components</p>', unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Core Components")
    st.markdown("""
    - **app.py**: Main Streamlit application
    - **qa_system.py**: RAG implementation
    - **financial_calc.py**: Financial analysis system
    - **data_processing.py**: Data pipeline utilities
    """)

with col2:
    st.markdown("#### Supporting Modules")
    st.markdown("""
    - **prompts.py**: LLM prompt engineering
    - **test_components.py**: Unit testing
    - **requirements.txt**: Dependency management
    - **README.md**: Setup instructions
    """)

# Setup Instructions
st.markdown("---")
st.markdown('<p class="medium-font">Setup Instructions</p>', unsafe_allow_html=True)
with st.container():
    st.markdown("""
    1. **Clone the Repository**
    ```bash
    git clone https://github.com/yourusername/hawker-guru
    cd hawker-guru
    ```

    2. **Set Up Virtual Environment**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\\Scripts\\activate
    ```

    3. **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

    4. **Run the Application**
    ```bash
    streamlit run app.py
    ```
    """)

# Note about Code Access
st.markdown("---")
st.info("""
**Note about Source Code Access**: 
The complete source code is available upon request. For access:
1. Visit the GitHub repository
2. Follow the repository for updates
3. Raise issues or feature requests through GitHub
4. Contact the maintainers for specific questions
""")