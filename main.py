import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from src.data_handlers.processor import setup_hawker_guru
import os
from dotenv import load_dotenv
from src.helper_functions.utility import check_password

# Check if the password is correct.
if not check_password():
    st.stop()

load_dotenv()

# region <--------- Data Loading and Helper Functions --------->
@st.cache_data
def load_data():
    """Load and preprocess hawker centre data"""
    df = pd.read_excel("data/HawkerCentres.xlsx")
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
    """Display the financial calculator interface with focus on determining sustainable rent"""
    st.markdown("### 🧮 Sustainable Bid Estimator")
    st.markdown("""
    This calculator will help you determine a logical monthly rent you can afford based on your estimated costs and revenue.
    All amounts should be entered excluding GST.
    """)
    
    # Initialize calculation results in session state if they don't exist
    if 'calc_results' not in st.session_state:
        st.session_state.calc_results = None
    
    with st.form("Sustainable Bid Estimator"):
        # Operational costs
        st.markdown("#### 1. Monthly Operating Costs")
        col1, col2 = st.columns(2)
        
        with col1:
            ingredients = st.number_input("Raw Materials & Ingredients (SGD)", 
                help="Cost of ingredients and raw materials needed for your dishes",
                min_value=0, value=3000)
            
            utilities = st.number_input("Utilities (SGD)",
                help="Estimated monthly utilities including electricity and water",
                min_value=0, value=500)
            
            sc_charges = st.number_input("Service & Conservancy Charges (SGD)",
                help="Monthly S&C charges for the stall",
                min_value=0, value=300)
        
        with col2:
            manpower = st.number_input("Manpower Cost (SGD)",
                help="Total monthly wages for all workers including yourself",
                min_value=0, value=2000)
            
            cleaning = st.number_input("Table Cleaning Charges (SGD)",
                help="Monthly charges for table cleaning service",
                min_value=0, value=200)
            
            misc_costs = st.number_input("Miscellaneous (SGD)",
                help="Other monthly expenses like maintenance, supplies, etc.",
                min_value=0, value=300)
        
        # Revenue estimation
        st.markdown("#### 2. Revenue Estimation")
        col3, col4 = st.columns(2)
        
        with col3:
            avg_price = st.number_input("Average Price per Item (SGD)",
                help="Average selling price of your items before GST",
                min_value=0.0, value=5.0)
            
            items_per_day = st.number_input("Estimated Items Sold per Day",
                help="Expected number of items you can sell per day",
                min_value=0, value=100)
        
        with col4:
            days_per_month = st.number_input("Operating Days per Month",
                help="Number of days you plan to operate per month",
                min_value=0, max_value=31, value=26)
        
        calculate = st.form_submit_button("Calculate Break-even Rent")
        
        if calculate:
            # Calculate monthly figures
            monthly_revenue = avg_price * items_per_day * days_per_month
            monthly_costs = ingredients + utilities + manpower + sc_charges + cleaning + misc_costs
            sustainable_rent = monthly_revenue - monthly_costs
            
            # Store results in session state
            st.session_state.calc_results = {
                'monthly_revenue': monthly_revenue,
                'monthly_costs': monthly_costs,
                'sustainable_rent': sustainable_rent,
                'items_per_day': items_per_day,
                'avg_price': avg_price,
                'days_per_month': days_per_month
            }
    
    # Display results outside the form
    if st.session_state.calc_results:
        results = st.session_state.calc_results
        
        st.markdown("### Monthly Break-even Analysis")
        
        # Key metrics in columns
        metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
        with metrics_col1:
            st.metric("Projected Revenue", f"${results['monthly_revenue']:,.2f}")
        with metrics_col2:
            st.metric("Operating Costs", f"${results['monthly_costs']:,.2f}")
        with metrics_col3:
            st.metric("Maximum Sustainable Rent", f"${results['sustainable_rent']:,.2f}")
        
        # Analysis and recommendations
        st.markdown("### Bidding Guidance")
        
        if results['sustainable_rent'] <= 0:
            st.error("""
            ⚠️ Warning: Your operating costs exceed projected revenue. 
            Consider reviewing your costs or revenue projections before proceeding with a bid.
            """)
        else:
            st.success(f"""
            Based on your projections, you could afford a maximum monthly rent of ${results['sustainable_rent']:,.2f} 
            while breaking even. For a sustainable business, consider bidding below this amount to ensure profitability.
            """)
            
            # Additional analysis
            st.markdown("### Additional Insights")
            st.markdown(f"""
            - Daily revenue needed to break even: ${(results['monthly_costs']/results['days_per_month']):.2f}
            - Minimum items to sell daily to break even: {(results['monthly_costs']/(results['avg_price'] * results['days_per_month'])):.0f} items
            - Current profit margin before rent: {((results['monthly_revenue'] - results['monthly_costs'])/results['monthly_revenue'] * 100):.1f}%
            """)
        
        # Add debug mode toggle
        debug_mode = st.sidebar.checkbox("Enable Debug Mode")
        
        # Expert analysis button outside the form
        if st.button("💡 Get Expert Analysis"):
            context = f"""
            Please analyze these financial projections for a hawker stall bidding decision:
            Monthly Revenue: \\${results['monthly_revenue']:,.0f}
            Monthly Operating Costs: \\${results['monthly_costs']:,.0f}
            Maximum Sustainable Rent: \\${results['sustainable_rent']:,.0f}
            Daily Items Sold: {results['items_per_day']}
            Average Price: \\${results['avg_price']:.2f}
            
            Provide a clear analysis following this EXACT format and indentation:

            1. Business Sustainability Analysis:
            - Comment on whether revenue can cover costs
            - State the profit margin

            2. Bidding Considerations:
            - Suggest a reasonable bid range
            - List key factors to consider

            3. Risks and Opportunities:
            Risks:
            - Risk point 1
            - Risk point 2
            - Risk point 3

            Opportunities:
            - Opportunity point 1
            - Opportunity point 2
            - Opportunity point 3
            
            Format Requirements:
            - Use proper indentation as shown above
            - Start each bullet point with a hyphen (-)
            - Write dollar amounts as \\$X,XXX
            - Use "between \\$X,XXX and \\$Y,XXX" for ranges
            - Round all numbers to whole dollars
            """
            
            with st.spinner('Analyzing your numbers...'):
                response = st.session_state.qa_chain.invoke({
                    "question": context,
                    "chat_history": []
                })
                
                # Clean up the response
                cleaned_response = (response['answer']
                    .replace('*', '')
                    .replace('#', '')
                    .replace('  ', ' ')
                    .replace(' ,', ',')
                    # Fix any inconsistent bullet points
                    .replace('•', '-')
                    .replace('* ', '- ')
                    # Ensure proper spacing after bullet points
                    .replace('-  ', '- ')
                    # Fix extra newlines
                    .replace('\n\n\n', '\n\n'))
                
                # Display in a structured way
                st.markdown("#### Expert Analysis")
                
                # Format the text as markdown to maintain hierarchy
                st.markdown(cleaned_response)
                
                if debug_mode:
                    st.markdown("### Debug View")
                    st.code(cleaned_response)



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
        st.markdown(f"**Number of {stalltype} Stalls in this centre:**\n{stall_count}")
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
        if st.button("🧮 Sustainable Bid Estimator", use_container_width=True):
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