import streamlit as st

# region <--------- Streamlit App Configuration --------->
st.set_page_config(
    page_title="About Hawker Guru",
    page_icon="🏪",
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
    </style>
""", unsafe_allow_html=True)

# Hero Section
st.markdown('<p class="big-font">Hawker Guru</p>', unsafe_allow_html=True)
st.markdown("### Empowering Informed Bidding for Singapore's Hawker Stalls")

# Project Scope
st.markdown("---")
st.markdown('<p class="medium-font">Project Scope</p>', unsafe_allow_html=True)
with st.container():
    st.markdown('<div class="highlight">', unsafe_allow_html=True)
    st.markdown("""
    Hawker Guru addresses the critical issue of inflated hawker stall tender bids in Singapore. The scope includes:
    
    - **Target Users**: 2,000-2,500 unique tenderers participating in monthly hawker stall tenders annually
    - **Focus Area**: Cooked food stall tender exercises
    - **Geographic Coverage**: Singapore Hawker Centres
    - **Time Frame**: Development for January 2025 tender exercise launch
    - **Problem Domain**: Bid price rationalization and business planning support
    """)
    st.markdown('</div>', unsafe_allow_html=True)

# Objectives
st.markdown("---")
st.markdown('<p class="medium-font">Objectives</p>', unsafe_allow_html=True)
with st.container():
    st.markdown("""
    1. **Primary Objective**
       - Empower hawker stall tenderers to make informed, rational bidding decisions
    
    2. **Secondary Objectives**
       - Reduce the risk of inflated tender prices
       - Safeguard the affordability of hawker food
       - Improve efficiency in the tender research process
       - Support sustainable business practices in the hawker trade
    
    3. **Success Metrics**
       - Reduction in outlier bid amounts
       - Increased user engagement with tender information
       - Positive user feedback on decision support tools
    """)

# Data Sources
st.markdown("---")
st.markdown('<p class="medium-font">Data Sources</p>', unsafe_allow_html=True)
with st.container():
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Primary Data Sources")
        st.markdown("""
        - NEA Tender Database
        - Historical bid records
        - Hawker center location data
        - Stall specifications
        - Tender requirements documentation
        """)
    
    with col2:
        st.markdown("#### Supporting Information")
        st.markdown("""
        - Market research reports
        - Industry guidelines
        - Regulatory frameworks
        - Operating costs benchmarks
        - Food industry statistics
        """)

# Features
st.markdown("---")
st.markdown('<p class="medium-font">Features</p>', unsafe_allow_html=True)

# Core Features
st.markdown("### Core Features")
col1, col2 = st.columns(2)

with col1:
    with st.container():
        st.markdown("#### 📚 Q&A System")
        st.markdown("""
        - RAG-powered information retrieval
        - Real-time query processing
        - Context-aware responses
        - Multi-lingual support
        - Source attribution
        """)

with col2:
    with st.container():
        st.markdown("#### 🧮 Financial Calculator")
        st.markdown("""
        - Bid price analysis
        - Cash flow projections
        - Break-even calculations
        - Operating cost estimates
        - Revenue forecasting
        """)

# Additional Features
st.markdown("### Additional Features")
with st.container():
    st.markdown("""
    - **User Management**
      - Personalized advice based on business type
      - Progress tracking
      - Saved calculations
    
    - **Data Visualization**
      - Historical bid trends
      - Market analysis graphs
      - Location-based insights
    
    - **Documentation**
      - Step-by-step guides
      - FAQ repository
      - Best practices
    """)