import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from processor import setup_hawker_guru
import os
from dotenv import load_dotenv
from helper_functions.utility import check_password

# Check if the password is correct.
if not check_password():
    st.stop()

load_dotenv()

# region <--------- Data Loading and Helper Functions --------->
@st.cache_data
def load_data():
    """Load and preprocess hawker centre data"""
    df = pd.read_excel("Data/HawkerCentres.xlsx")
    df.columns = df.columns.str.strip()
    return df

def get_stall_count(df, hawker_centre, stall_type):
    """Get the number of stalls for a specific hawker centre and stall type"""
    stall_type_map = {
        'COOKED FOOD': 'Cooked Food',
        'LOCK-UP': 'Locked-Up',
        'MARKET SLAB': 'Market Slab',
        'KIOSK': 'Kiosks'
    }
    
    column = stall_type_map.get(stall_type)
    if column:
        count = df[df['Hawker Centre'] == hawker_centre][column].iloc[0]
        return 0 if pd.isna(count) else int(count)
    return 0

def get_landlord(df, hawker_centre):
    """Get the landlord for a specific hawker centre"""
    return df[df['Hawker Centre'] == hawker_centre]['Landlord'].iloc[0]

# region <--------- Chat Functions --------->

def initialize_chat_state():
    """Initialize chat-related session state variables"""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'chat_started' not in st.session_state:
        st.session_state.chat_started = False
    if 'calculator_started' not in st.session_state:
        st.session_state.calculator_started = False
    if 'qa_chain' not in st.session_state:
        st.session_state.qa_chain = setup_hawker_guru()

def display_chat_interface():
    """Display the chat interface"""
    st.markdown("### 💬 Chat with Hawker Guru")
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about bidding, regulations, or costs..."):
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Prepare the context-enriched prompt
        context = f"""You are Hawker Guru, a helpful assistant for Singapore hawker stall bidding. 
        When answering questions, follow these guidelines:

        1. For general questions about tendering process, requirements, or guidelines:
           - First provide the general information from the tender notice and guidelines
           - Only mention location-specific details if they are directly relevant to the question
           - Do not restrict your answer to the currently selected location unless specifically asked

        2. For questions about Articles of Sale (AOS):
           - First provide the general rules from the AOS guide
           - Only then mention any location-specific restrictions if relevant

        3. For questions specifically about the selected location:
           - Hawker Centre: {st.session_state.selected_hawkercentre}
           - Stall Type: {st.session_state.selected_stalltype}
           - Number of Stalls: {get_stall_count(df_hawkercentres, st.session_state.selected_hawkercentre, st.session_state.selected_stalltype)}
           - Landlord: {get_landlord(df_hawkercentres, st.session_state.selected_hawkercentre)}

        Current user's question seems to be about: {prompt}
        
        Provide a comprehensive answer that prioritizes relevant general information first, 
        followed by specific details only when they add value to the response.
        """
        
        # Generate response using qa_chain
        with st.spinner('Thinking...'):
            response = st.session_state.qa_chain.invoke({
                "question": context,
                "chat_history": st.session_state.messages
            })
            
            # Debug: Print sources used
            print("\nSources used for response:")
            for doc in response['source_documents']:
                print(f"Source type: {doc.metadata.get('type', 'unknown')}")
                print(f"Content preview: {doc.page_content[:100]}...")
            
            # Update messages for next interaction
            st.session_state.messages.append((prompt, response['answer']))
            
            # Add assistant response to chat history
            st.session_state.chat_history.append({
                "role": "assistant", 
                "content": response['answer']
            })
        
        st.rerun()

# region <--------- Financial Calculator Functions --------->
def display_financial_calculator():
    """Display the financial calculator interface"""
    st.markdown("### 🧮 Financial Calculator")
    
    with st.form("financial_calculator"):
        # Monthly Costs
        st.subheader("Monthly Cost Estimation")
        
        # Rental costs
        st.markdown("#### 1. Rental Costs")
        proposed_bid = st.number_input("Proposed Monthly Bid (SGD)", min_value=0, value=1500)
        
        # Operational costs
        st.markdown("#### 2. Operational Costs")
        col1, col2 = st.columns(2)
        with col1:
            ingredients = st.number_input("Raw Materials & Ingredients (SGD)", min_value=0, value=3000)
            utilities = st.number_input("Utilities (SGD)", min_value=0, value=500)
        with col2:
            labor = st.number_input("Labor (SGD)", min_value=0, value=2000)
            misc_costs = st.number_input("Miscellaneous (SGD)", min_value=0, value=300)
        
        # Revenue estimation
        st.markdown("#### 3. Revenue Estimation")
        col3, col4 = st.columns(2)
        with col3:
            avg_price = st.number_input("Average Price per Item (SGD)", min_value=0.0, value=5.0)
            items_per_day = st.number_input("Estimated Items Sold per Day", min_value=0, value=100)
        with col4:
            days_per_month = st.number_input("Operating Days per Month", min_value=0, max_value=31, value=26)
        
        calculate = st.form_submit_button("Calculate Projections")
        
        if calculate:
            monthly_revenue = avg_price * items_per_day * days_per_month
            monthly_costs = proposed_bid + ingredients + utilities + labor + misc_costs
            monthly_profit = monthly_revenue - monthly_costs
            profit_margin = (monthly_profit / monthly_revenue) * 100 if monthly_revenue > 0 else 0
            
            # Display results
            st.markdown("### Monthly Projection")
            metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
            with metrics_col1:
                st.metric("Revenue", f"${monthly_revenue:,.2f}")
            with metrics_col2:
                st.metric("Costs", f"${monthly_costs:,.2f}")
            with metrics_col3:
                st.metric("Net Profit", f"${monthly_profit:,.2f}")
            
            # Analysis
            st.markdown("### Analysis")
            if profit_margin < 10:
                st.warning(f"⚠️ Low profit margin ({profit_margin:.1f}%). Consider reviewing your costs or pricing strategy.")
            elif profit_margin > 30:
                st.success(f"✅ Healthy profit margin ({profit_margin:.1f}%) projected.")
            
            st.markdown(f"""
            **Key Metrics:**
            - Break-even Sales per Day: ${(monthly_costs/days_per_month):.2f}
            - Required Items Sold to Break-even: {(monthly_costs/(avg_price * days_per_month)):.0f} items/day
            - Current Profit per Item: ${(monthly_profit/(items_per_day * days_per_month)):.2f}
            """)

# region <--------- Main App --------->
def main():
    # Page config
    st.set_page_config(
        page_title="HawkerGuru",
        page_icon="🏪",
        layout="wide"
    )
    
    # Custom CSS
    st.markdown("""
        <style>
        .big-font {
            font-size:40px !important;
            font-weight:bold;
        }
        .stall-info {
            padding: 20px;
            background-color: #f0f2f6;
            border-radius: 10px;
            margin: 10px 0px;
        }
        .landlord-info {
            padding: 15px;
            background-color: #e8f4ea;
            border-radius: 10px;
            margin: 10px 0px;
        }
        </style>
    """, unsafe_allow_html=True)

    # Initialize states
    initialize_chat_state()
    
    # Title
    st.markdown('<p class="big-font">🏪 Hawker Guru</p>', unsafe_allow_html=True)
    st.markdown("### Your Guide to Singapore Hawker Stall Bidding")
    
    # Disclaimer handling
    with st.expander("⚠️ **IMPORTANT DISCLAIMER** - Please Read", expanded=True):
        st.markdown("""
        **IMPORTANT NOTICE:** This web application is developed as a proof-of-concept prototype. 
        The information provided here is **NOT intended for actual usage** and should not be relied upon 
        for making any decisions, especially those related to financial, legal, or healthcare matters.

        **Furthermore, please be aware that the LLM may generate inaccurate or incorrect information. 
        You assume full responsibility for how you use any generated output.**

        Always consult with qualified professionals for accurate and personalized advice.
        """)
        
        if 'disclaimer_accepted' not in st.session_state:
            st.session_state.disclaimer_accepted = False
        
        st.session_state.disclaimer_accepted = st.checkbox(
            "I have read and understood this disclaimer",
            value=st.session_state.disclaimer_accepted
        )

    if not st.session_state.disclaimer_accepted:
        st.warning("Please read and acknowledge the disclaimer above to proceed.")
        st.stop()

    # Load data
    global df_hawkercentres
    df_hawkercentres = load_data()
    hawker_list = sorted(df_hawkercentres["Hawker Centre"].tolist())

    # Selection interface
    col1, col2 = st.columns(2)
    with col1:
        if 'selected_hawkercentre' not in st.session_state:
            st.session_state.selected_hawkercentre = hawker_list[0]
        hawkercentre = st.selectbox('Select Hawker Centre', hawker_list, key='selected_hawkercentre')

    with col2:
        if 'selected_stalltype' not in st.session_state:
            st.session_state.selected_stalltype = 'COOKED FOOD'
        stalltype = st.selectbox('Select Stall Type', ('COOKED FOOD', 'LOCK-UP', 'MARKET SLAB','KIOSK'), key='selected_stalltype')

    # Location details
    st.markdown("---")
    st.markdown("### Selected Location Details")
    
    info_col1, info_col2 = st.columns(2)
    with info_col1:
        st.markdown('<div class="stall-info">', unsafe_allow_html=True)
        st.markdown(f"**Selected Hawker Centre:**\n{hawkercentre}")
        st.markdown(f"**Stall Type:**\n{stalltype}")
        stall_count = get_stall_count(df_hawkercentres, hawkercentre, stalltype)
        st.markdown(f"**Number of {stalltype} Stalls:**\n{stall_count}")
        st.markdown('</div>', unsafe_allow_html=True)

    with info_col2:
        st.markdown('<div class="landlord-info">', unsafe_allow_html=True)
        landlord = get_landlord(df_hawkercentres, hawkercentre)
        st.markdown("**Landlord Details**")
        st.markdown(f"This hawker centre is managed by:\n{landlord}")
        st.markdown('</div>', unsafe_allow_html=True)

    # Action buttons
    st.markdown("---")
    button_col1, button_col2 = st.columns(2)
    
    with button_col1:
        if st.button("💬 Chat with Hawker Guru", use_container_width=True):
            st.session_state.chat_started = True
            st.session_state.calculator_started = False
    
    with button_col2:
        if st.button("🧮 Financial Calculator", use_container_width=True):
            st.session_state.calculator_started = True
            st.session_state.chat_started = False

    # Display appropriate interface based on selection
    if st.session_state.chat_started:
        display_chat_interface()
    elif st.session_state.calculator_started:
        display_financial_calculator()
    else:
        st.info("""
            👆 Select a hawker centre and stall type above, then:
            - Use the **Chat** feature to ask questions about the tender process
            - Use the **Calculator** to estimate your business costs and potential returns
            """)

if __name__ == "__main__":
    main()