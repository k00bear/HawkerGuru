import streamlit as st

# Configure the page
st.set_page_config(
    page_title="About HawkerGuru",
    page_icon="🏪",
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
    </style>
""", unsafe_allow_html=True)

# Hero Section
st.markdown('<p class="big-font">🏪 About HawkerGuru</p>', unsafe_allow_html=True)
st.markdown("### The Smart Assistant to Bidding for a Hawker Stall")

# Project Scope
st.markdown("---")
st.markdown('<p class="medium-font">Project Scope</p>', unsafe_allow_html=True)
with st.container():
    st.markdown("""
    HawkerGuru addresses the critical issue of inflated hawker stall tender bids in Singapore:
    
    - **Target Users**: 4,000-4,500 unique tenderers participating in monthly hawker stall tenders annually
    - **Focus Area**: Empowering informed bidding through the use of AI
    - **Geographic Coverage**: Singapore's Hawker Centres
    - **Problem Domain**: Bid price rationalization and business planning support
    """)

# Objectives
st.markdown("---")
st.markdown('<p class="medium-font">Objectives</p>', unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    #### Primary Objectives
    - Empower hawker stall tenderers to make informed, rational bidding decisions
    - Improve efficiency in the tender research process
    
    #### Secondary Objectives
    - Reduce the risk of inflated tender prices
    - Safeguard the affordability of hawker food
    - Support sustainable business practices in the hawker trade
    """)

with col2:
    st.info("""
    ℹ️ HawkerGuru uses advanced AI technology to provide accurate information from official sources. 
    All responses are based on current tender documentation and regulations.
    """)

# Data Sources
st.markdown("---")
st.markdown('<p class="medium-font">Data Sources</p>', unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Core Documents")
    st.markdown("""
    - Tender notices and FAQs
    - Terms and conditions of Tender
    - Articles of sale regulations
    - Things to note when tendering
    """)

with col2:
    st.markdown("#### Supporting Information")
    st.markdown("""
    - Hawker centre locations and details
    - Stall types and counts
    - Centre-specific information
    """)

# Features
st.markdown("---")
st.markdown('<p class="medium-font">Features</p>', unsafe_allow_html=True)

# Core Features
st.markdown("### Core Features")
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 💬 Information Access System")
    st.markdown("""
    - Instant access to tender regulations and guidelines
    - AI-powered assistance for tender-related queries
    - Location-specific requirements and restrictions
    - Articles of sale guidance
    - Sourced answers from official documents
    """)

with col2:
    st.markdown("#### 🧮 Financial Calculator")
    st.markdown("""
    - Monthly revenue and cost projections
    - Break-even rent calculation
    - Operating cost breakdown analysis
    - Simple business review
    - Sustainable bid range recommendations
    """)

# Additional Features
st.markdown("### Support Features")
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 📊 Data Visualization")
    st.markdown("""
    - Interactive location maps with radius search
    - Nearby centres visualization
    - Stall count information
    - Centre-specific details
    """)

with col2:
    st.markdown("#### 🎯 Intelligent Analysis")
    st.markdown("""
    - Location-based insights
    - Business viability assessment
    - Custom recommendations
    - Risk evaluation
    """)

# Footer with project attribution
st.markdown("---")
st.caption("Made with ❤️ by koobear | AI Champions Bootcamp 2024 Graduation Project | © 2024")