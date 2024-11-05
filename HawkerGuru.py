"""
HawkerGuru - Main Application
A Streamlit application for Singapore hawker stall bidding guidance.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import folium
from streamlit_folium import st_folium
from datetime import datetime
import os
from dotenv import load_dotenv
from math import radians, sin, cos, sqrt, atan2

from src.qa.qa_chain import setup_hawker_guru
from src.helper_functions.utility import check_password
from src.models.data_models import LocationDetails, NearbyCenter, CalculationResults

# Constants
RADIUS_OPTIONS = [0.5, 1, 1.5, 2, 2.5, 3, 5]  # kilometers
STALL_TYPES = ('COOKED FOOD', 'LOCK-UP', 'MARKET SLAB', 'KIOSK')
DEFAULT_RADIUS = 2  # kilometers

class SessionState:
    """Manages application session state."""
    
    @staticmethod
    def initialize() -> None:
        """Initialize all session state variables."""
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
        if 'disclaimer_accepted' not in st.session_state:
            st.session_state.disclaimer_accepted = False
        if 'calc_results' not in st.session_state:
            st.session_state.calc_results = None

class DataLoader:
    """Handles data loading and processing operations."""
    
    @staticmethod
    @st.cache_data
    def load_hawker_data() -> pd.DataFrame:
        """Load and preprocess hawker centre data."""
        df = pd.read_excel("data/HawkerCentres.xlsx")
        df.columns = df.columns.str.strip()
        return df
    
    @staticmethod
    def get_stall_count(df: pd.DataFrame, hawker_centre: str, stall_type: str) -> int:
        """Get the number of stalls for a specific hawker centre and stall type."""
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
    
    @staticmethod
    def get_location_details(df: pd.DataFrame, hawker_centre: str) -> LocationDetails:
        """Get location details for a specific hawker centre."""
        center_data = df[df['Hawker Centre'] == hawker_centre].iloc[0]
        return LocationDetails(
            latitude=center_data['Latitude'],
            longitude=center_data['Longitude'],
            address=center_data['Address'],
            postal_code=center_data['Postal_Code']
        )
    
    @staticmethod
    def get_landlord(df: pd.DataFrame, hawker_centre: str) -> str:
        """Get the landlord for a specific hawker centre."""
        return df[df['Hawker Centre'] == hawker_centre]['Landlord'].iloc[0]

class LocationService:
    """Handles location-based calculations and operations."""
    
    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate the distance between two points using the Haversine formula."""
        R = 6371  # Earth's radius in kilometers
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        return R * c
    
    @classmethod
    def get_nearby_centres(cls, df: pd.DataFrame, selected_centre: str, 
                          radius_km: float) -> List[NearbyCenter]:
        """Find all hawker centres within the specified radius."""
        center_data = df[df['Hawker Centre'] == selected_centre].iloc[0]
        center_lat = center_data['Latitude']
        center_lon = center_data['Longitude']
        
        nearby_centres = []
        for idx, row in df.iterrows():
            if (row['Hawker Centre'] != selected_centre and 
                pd.notna(row['Latitude']) and pd.notna(row['Longitude'])):
                distance = cls.calculate_distance(
                    center_lat, center_lon,
                    row['Latitude'], row['Longitude']
                )
                if distance <= radius_km:
                    nearby_centres.append(NearbyCenter(
                        name=row['Hawker Centre'],
                        distance=distance,
                        lat=row['Latitude'],
                        lon=row['Longitude']
                    ))
        
        return sorted(nearby_centres, key=lambda x: x.distance)

class MapService:
    """Handles map creation and visualization."""
    
    @staticmethod
    def create_interactive_map(selected_centre: str, nearby_centres: List[NearbyCenter],
                             location_details: LocationDetails, radius_km: float,
                             df: pd.DataFrame) -> folium.Map:
        """Create an interactive map with markers and radius circle."""
        m = folium.Map(
            location=[location_details.latitude, location_details.longitude],
            zoom_start=12,  # Changed from 13 to 12
            tiles="CartoDB positron"
        )
        
        # Add radius circle
        folium.Circle(
            location=[location_details.latitude, location_details.longitude],
            radius=radius_km * 1000,
            color='#6B7280',
            weight=1,
            fill=True,
            fill_color='#3B82F6',
            fill_opacity=0.15,
            popup=folium.Popup(f'<div style="text-align: center;"><b>{radius_km}km radius</b></div>')
        ).add_to(m)
        
        # Add selected centre marker
        stall_info = MapService._get_stall_counts(df, selected_centre)
        selected_popup_html = f"""
        <div style='width: 200px'>
            <b>{selected_centre}</b><br>
            {location_details.address} Singapore {location_details.postal_code}<Br>
            <br>
            <b>Stall Count:</b><br>
            {stall_info}
        </div>
        """

        folium.CircleMarker(
            location=[location_details.latitude, location_details.longitude],
            radius=10,
            popup=folium.Popup(selected_popup_html, max_width=300),
            color='#DC2626',
            fill=True,
            fill_color='#DC2626',
            fill_opacity=0.7,
            weight=2,
            z_index_offset=1000
        ).add_to(m)
        
        # Add nearby centres
        for centre in nearby_centres:
            nearby_stall_info = MapService._get_stall_counts(df, centre.name)
            popup_html = f"""
            <div style='width: 200px'>
                <b>{centre.name}</b><br>
                Distance from selected: {centre.distance:.1f} km<br>
                <br>
                <b>Stall Count:</b><br>
                {nearby_stall_info}
            </div>
            """
            
            folium.CircleMarker(
                location=[centre.lat, centre.lon],
                radius=8,
                popup=folium.Popup(popup_html, max_width=300),
                color='#2563EB',
                fill=True,
                fill_color='#2563EB',
                fill_opacity=0.7,
                weight=2
            ).add_to(m)
        
        # Calculate bounds to fit the radius circle
        circle_bounds = [
            [location_details.latitude - (radius_km/111), location_details.longitude - (radius_km/111)],  # SW corner
            [location_details.latitude + (radius_km/111), location_details.longitude + (radius_km/111)]   # NE corner
        ]
        
        # Fit map to show the circle with padding
        m.fit_bounds(circle_bounds, padding=[30, 30])
        
        return m
    
    @staticmethod
    def _get_stall_counts(df: pd.DataFrame, centre_name: str) -> str:
        """Helper method to get formatted stall counts for a centre."""
        try:
            centre_data = df[df['Hawker Centre'] == centre_name].iloc[0]
            stall_counts = []
            
            # Map of column names to display names
            stall_types = {
                'Cooked Food': 'Cooked Food Stalls',
                'Locked-Up': 'Lock-up Stalls',
                'Market Slab': 'Market Slab Stalls',
                'Kiosks': 'Kiosks'
            }
            
            # Get counts for each stall type
            for col, display_name in stall_types.items():
                count = centre_data.get(col, 0)
                if pd.notna(count) and count > 0:
                    stall_counts.append(f"• {display_name}: {int(count)}")
            
            return "<br>".join(stall_counts) if stall_counts else "No stall information available"
            
        except (KeyError, IndexError):
            return "Stall information not available"

class ChatInterface:
    """Handles chat interface and interactions."""
    
    @staticmethod
    def display_chat_interface(df: pd.DataFrame, hawker_centre: str, stall_type: str) -> None:
        """Display and handle the chat interface."""
        st.markdown("### 💬 Chat with HawkerGuru")
        
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        if prompt := st.chat_input("Ask about bidding, regulations, or costs..."):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            
            context = ChatInterface._build_chat_context(df, hawker_centre, stall_type, prompt)
            
            with st.spinner('Thinking...'):
                response = st.session_state.qa_chain.invoke({
                    "question": context,
                    "chat_history": st.session_state.messages
                })
                
                st.session_state.messages.append((prompt, response['answer']))
                st.session_state.chat_history.append({
                    "role": "assistant", 
                    "content": response['answer']
                })
            
            st.rerun()
    
    @staticmethod
    def _build_chat_context(df: pd.DataFrame, hawker_centre: str, 
                           stall_type: str, prompt: str) -> str:
        """Build context for the chat interaction."""
        return f"""You are HawkerGuru, a helpful assistant for Singapore hawker stall bidding. 
        When answering questions, follow these guidelines:

        1. For general questions about tendering process, requirements, or guidelines:
           - First provide the general information from the tender notice and guidelines
           - Only mention location-specific details if they are directly relevant to the question
           - Do not restrict your answer to the currently selected location unless specifically asked

        2. For questions about Articles of Sale (AOS):
           - First provide the general rules from the AOS guide
           - Only then mention any location-specific restrictions if relevant

        3. For questions specifically about the selected location:
           - Hawker Centre: {hawker_centre}
           - Stall Type: {stall_type}
           - Number of Stalls: {DataLoader.get_stall_count(df, hawker_centre, stall_type)}
           - Landlord: {DataLoader.get_landlord(df, hawker_centre)}

        Current user's question seems to be about: {prompt}
        
        Provide a comprehensive answer that prioritizes relevant general information first, 
        followed by specific details only when they add value to the response.
        """

class FinancialCalculator:
    """Handles rental calculations and financial projections."""
    
    @staticmethod
    def calculate_financials(revenue_params: Dict, cost_params: Dict) -> CalculationResults:
        """Calculate financial metrics."""
        # Calculate monthly revenue
        monthly_revenue = (revenue_params['avg_price'] * 
                        revenue_params['items_per_day'] * 
                        revenue_params['days_per_month'])
        
        # Calculate total monthly costs excluding rent
        operating_costs = sum(value for key, value in cost_params.items() 
                            if key != 'personal_income')
        
        # Total costs including personal income
        total_monthly_costs = operating_costs + cost_params['personal_income']
        
        # Calculate sustainable rent (revenue minus all costs including personal income)
        sustainable_rent = monthly_revenue - total_monthly_costs
        
        return CalculationResults(
            monthly_revenue=monthly_revenue,
            monthly_costs=total_monthly_costs,
            sustainable_rent=sustainable_rent,
            items_per_day=revenue_params['items_per_day'],
            avg_price=revenue_params['avg_price'],
            days_per_month=revenue_params['days_per_month'],
            personal_income=cost_params['personal_income'],
            costs_breakdown=cost_params
        )
    
    @staticmethod
    def display_calculator() -> None:
        """Display the financial calculator interface."""
        st.markdown("### 🧮 Sustainable Bid Calculator")
        st.markdown("""
        Find out the maximum monthly rent you can afford before your business starts losing money. Since your bid amount 
        becomes your monthly rent, this calculator helps you:
        - Calculate your break-even point based on expected costs and revenue
        - Determine a sustainable bid amount that keeps your business profitable
        - Avoid overbidding that could strain your business finances
        
        *Note: Please enter all amounts excluding GST.*
        """)
        
        with st.form("Sustainable Bid Calculator"):
            cost_params = FinancialCalculator._get_cost_inputs()
            revenue_params = FinancialCalculator._get_revenue_inputs()
            
            if st.form_submit_button("Calculate Break-even Rent"):
                results = FinancialCalculator.calculate_financials(revenue_params, cost_params)
                st.session_state.calc_results = results
        
        if st.session_state.calc_results:
            FinancialCalculator._display_results(st.session_state.calc_results)
    
    @staticmethod
    def _get_cost_inputs() -> Dict:
        """Get cost inputs from user."""
        st.markdown("#### 1. Monthly Operating Costs")
        
        st.markdown("##### Essential Income")
        personal_income = st.number_input(
            "Your Target Monthly Income (SGD)",
            help="How much you need to earn monthly to support yourself/family",
            min_value=0,
            value=2500,
            step=100
        )
        
        st.markdown("##### Operating Expenses")
        col1, col2 = st.columns(2)
        
        with col1:
            ingredients = st.number_input(
                "Raw Materials & Ingredients (SGD)", 
                min_value=0, 
                value=3000
            )
            utilities = st.number_input(
                "Utilities (SGD)", 
                min_value=0, 
                value=500
            )
            sc_charges = st.number_input(
                "Service & Conservancy Charges (SGD)", 
                min_value=0, 
                value=300
            )
        
        with col2:
            manpower = st.number_input(
                "Manpower Cost (SGD)", 
                min_value=0, 
                value=2000
            )
            cleaning = st.number_input(
                "Table Cleaning Charges (SGD)", 
                min_value=0, 
                value=200
            )
            misc_costs = st.number_input(
                "Miscellaneous (SGD)", 
                min_value=0, 
                value=300
            )
        
        return {
            'personal_income': personal_income,
            'ingredients': ingredients,
            'utilities': utilities,
            'sc_charges': sc_charges,
            'manpower': manpower,
            'cleaning': cleaning,
            'misc_costs': misc_costs
        }
    
    @staticmethod
    def _get_revenue_inputs() -> Dict:
        """Get revenue inputs from user."""
        st.markdown("#### 2. Revenue Estimation")
        col1, col2 = st.columns(2)
        
        with col1:
            avg_price = st.number_input("Average Price per Item (SGD)", 
                min_value=0.0, value=5.0)
            items_per_day = st.number_input("Estimated Items Sold per Day", 
                min_value=0, value=100)
        
        with col2:
            days_per_month = st.number_input("Operating Days per Month",
                min_value=0, max_value=31, value=24)
        
        return {
            'avg_price': avg_price,
            'items_per_day': items_per_day,
            'days_per_month': days_per_month
        }

    @staticmethod
    def _display_results(results: CalculationResults) -> None:
        """Display calculation results."""
        st.info("""
        ℹ️ **Important Note**
                
        This calculator helps you understand your business finances and shows the maximum monthly rent you can afford 
        while ensuring you earn your target monthly income. For a safer bid, consider offering 20-30% below this maximum. 
        
        **Remember**: The final bidding decision is yours. Many factors affect business success, and market conditions can vary. 
        Use these insights as one of many tools in your decision-making process.
        """)
        
        st.markdown("### Monthly Break-even Analysis")
        
        # Display key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Monthly Revenue", 
                f"${results.monthly_revenue:,.2f}",
                help="Expected monthly revenue based on your sales projections"
            )
        
        with col2:
            operating_costs = sum(value for key, value in results.costs_breakdown.items() 
                                if key != 'personal_income')
            st.metric(
                "Operating Costs", 
                f"${operating_costs:,.2f}",
                help="Total monthly operating expenses excluding your income"
            )
        
        with col3:
            st.metric(
                "Your Income", 
                f"${results.personal_income:,.2f}",
                help="Your target monthly income"
            )
        
        with col4:
            st.metric(
                "Maximum Bid",
                f"${results.sustainable_rent:,.2f}",
                help="Maximum monthly rent you can afford while meeting your income target"
            )
        
        # Analysis and recommendations
        if results.sustainable_rent <= 0:
            st.error("""
            ⚠️ **Warning**: With current projections, the business cannot support your income target.
            
            Consider these adjustments:
            1. Increase average selling price
            2. Increase daily sales target
            3. Reduce operating costs where possible
            4. Adjust your monthly income target
            """)
        else:
            recommended_bid = results.sustainable_rent * 0.75  # 25% safety margin
            st.success(f"""
            ✅ **Bid Recommendation**:
            - Maximum affordable rent: \\${results.sustainable_rent:,.2f}
            - Recommended bid range: \\${recommended_bid:.2f} - \\${results.sustainable_rent:,.2f}
            - This ensures you'll earn your target monthly income of \\${results.personal_income:,.2f}
            """)
            
            # Add safety note
            st.info("""
            💡 **Safety Tip**: 
            Bidding below the maximum gives you a safety margin for:
            - Slower months
            - Unexpected expenses
            - Business adjustments
            """)
            
        FinancialCalculator._offer_simple_review(results)

    @staticmethod
    def _offer_simple_review(results: CalculationResults) -> None:
        """Offer simplified expert review of financial projections."""
        # Create some spacing before the review button
        st.markdown("---")
        
        if st.button("💡 Get Simple Business Review"):
            # Prepare the context for the AI
            context = f"""
            Based on these numbers:
            - Selling {results.items_per_day} items per day
            - At \\${results.avg_price:.2f} per item
            - Operating {results.days_per_month} days monthly
            - Aiming to earn \\${results.personal_income:,.2f} monthly
            - Total monthly costs: \\${results.monthly_costs:,.2f}
            - Expected monthly revenue: \\${results.monthly_revenue:,.2f}
            
            Provide a very simple, practical review in exactly this format:
            
            1. "Can this business work?"
            Give a straightforward yes/no/maybe answer with one simple reason.
            
            2. "Is your sales target realistic?"
            Comment if selling {results.items_per_day} items daily is reasonable for a hawker stall.
            
            3. "One thing to watch out for"
            Highlight the single most important risk or concern.
            
            4. "One suggestion to consider"
            Provide one practical suggestion to improve the business plan.
            
            Use simple language that a hawker would understand. Avoid business jargon.
            Keep each answer to 1-2 short sentences only.
            Base your answers on typical hawker stall operations in Singapore.
            """
            
            # Show loading spinner while getting review
            with st.spinner('Reviewing your numbers...'):
                response = st.session_state.qa_chain.invoke({
                    "question": context,
                    "chat_history": []
                })
                
                # Create a clean layout for the review
                st.markdown("#### 👀 Simple Business Review")
                
                # Add some style to the review
                styled_response = response['answer'].replace(
                    '1. "Can this business work?"',
                    '##### 1. Can this business work? 🤔'
                ).replace(
                    '2. "Is your sales target realistic?"',
                    '##### 2. Is your sales target realistic? 🎯'
                ).replace(
                    '3. "One thing to watch out for"',
                    '##### 3. One thing to watch out for ⚠️'
                ).replace(
                    '4. "One suggestion to consider"',
                    '##### 4. One suggestion to consider 💡'
                )
                
                st.markdown(styled_response)
                
                # Add reminder about the review's limitations
                st.info("""
                💡 **Remember**: 
                This is just a general review based on typical hawker businesses. 
                Your actual results may vary depending on your:
                - Location
                - Type of food
                - Cooking skills and experience
                - Customer service
                - Competition in the area
                """)

class UIComponents:
    """Handles UI components and styling."""
    
    @staticmethod
    def load_css() -> None:
        """Load custom CSS styles."""
        st.markdown("""
        <style>
        .big-font {
            font-size:40px !important;
            font-weight:bold;
        }
        .stColumn > div {
            padding: 0 !important;
        }
        .stall-info {
            padding: 20px;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            margin: 0;
            background-color: white;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .nearby-centre {
            padding: 8px 12px;
            margin: 5px 0;
            border: 1px solid #e2e8f0;
            border-radius: 5px;
            background-color: white;
        }
        .stSlider {
            margin: 0 !important;
            padding-bottom: 1rem !important;
        }
        .map-container {
            width: 100%;
            margin: 0;
            padding: 1rem;
            border-radius: 10px;
            background: white;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .stFoliumMap {
            width: 100% !important;
        }
        .stFoliumMap > iframe {
            width: 100% !important;
            height: 700px !important;
            border-radius: 8px !important;
        }
        div[data-testid="stSelectSlider"] {
            margin-bottom: 0 !important;
            padding-bottom: 0 !important;
        }
        </style>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def show_footer() -> None:
        """Display footer with attribution."""
        footer_html = """
        <div class="footer">
            Made with ❤️ by koobear | ABC2024 Graduation Project | © 2024
        </div>
        """
        st.markdown(footer_html, unsafe_allow_html=True)

    @staticmethod
    def show_disclaimer() -> bool:
        """Display and handle disclaimer acceptance."""
        with st.expander("⚠️ **IMPORTANT DISCLAIMER** - Please Read", expanded=True):
            st.markdown("""
            **IMPORTANT NOTICE:** This web application is developed as a proof-of-concept prototype. 
            The information provided here is **NOT intended for actual usage** and should not be relied 
            upon for making any decisions, especially those related to financial, legal, or healthcare 
            matters.

            **Furthermore, please be aware that the LLM may generate inaccurate or incorrect information. 
            You assume full responsibility for how you use any generated output.**

            Always consult with qualified professionals for accurate and personalized advice.
            """)
            
            st.session_state.disclaimer_accepted = st.checkbox(
                "I have read and understood this disclaimer",
                value=st.session_state.disclaimer_accepted
            )
            
            return st.session_state.disclaimer_accepted

class HawkerGuruApp:
    """Main application class."""
    
    def __init__(self):
        """Initialize the application."""
        self.setup_app()
        self.df = DataLoader.load_hawker_data()
        SessionState.initialize()
    
    def setup_app(self) -> None:
        """Configure the Streamlit application."""
        st.set_page_config(
            page_title="HawkerGuru",
            page_icon="🏪",
            layout="wide"
        )
        UIComponents.load_css()
    
    def run(self) -> None:
        """Run the main application."""
        st.markdown('<p class="big-font">🏪 HawkerGuru</p>', unsafe_allow_html=True)
        st.markdown("### Your Smart Assistant to Bidding for a Hawker Stall")
        
        if not UIComponents.show_disclaimer():
            st.warning("Please read and acknowledge the disclaimer above to proceed.")
            UIComponents.show_footer()  # Show footer even when disclaimer isn't accepted
            return
        
        hawker_list = sorted(self.df["Hawker Centre"].tolist())
        self._display_selection_interface(hawker_list)
        self._display_location_details()
        self._display_action_buttons()
        
        main_content = st.container()
        with main_content:
            if st.session_state.chat_started:
                ChatInterface.display_chat_interface(
                    self.df, 
                    st.session_state.selected_hawkercentre, 
                    st.session_state.selected_stalltype
                )
            elif st.session_state.calculator_started:
                FinancialCalculator.display_calculator()
            else:
                st.info("""
                    ✨ Ready to help you with your hawker stall tender! Choose one of these options:
                    
                    💬 **Ask Questions**
                    Click "Chat with HawkerGuru" to get answers about:
                    - Tender requirements and rules
                    - What you can sell in different stalls
                    - Location-specific guidelines
                    
                    🧮 **Plan Your Bid**
                    Click "Sustainable Bid Calculator" to:
                    - Calculate a suitable rental bid based on your business plan
                    - Estimate your monthly costs and revenue
                    - Check if your planned rental is affordable
                    """)
            
        UIComponents.show_footer()
    
    def _display_selection_interface(self, hawker_list: List[str]) -> None:
        """Display hawker centre and stall type selection interface."""
        col1, col2 = st.columns(2)
        with col1:
            if 'selected_hawkercentre' not in st.session_state:
                st.session_state.selected_hawkercentre = hawker_list[0]
            st.selectbox('Select Hawker Centre', hawker_list, key='selected_hawkercentre')
        
        with col2:
            if 'selected_stalltype' not in st.session_state:
                st.session_state.selected_stalltype = STALL_TYPES[0]
            st.selectbox('Select Stall Type', STALL_TYPES, key='selected_stalltype')
    
    def _display_location_details(self) -> None:
        """Display location details and map."""
        st.markdown("---")
        st.markdown("### Selected Hawker Centre Details")
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            selected_radius = st.select_slider(
                "Show nearby hawker centres in blue dots within radius (km):",
                options=RADIUS_OPTIONS,
                value=DEFAULT_RADIUS
            )
            
            location_details = DataLoader.get_location_details(
                self.df, 
                st.session_state.selected_hawkercentre
            )
            
            if pd.notna(location_details.latitude) and pd.notna(location_details.longitude):
                nearby = LocationService.get_nearby_centres(
                    self.df,
                    st.session_state.selected_hawkercentre,
                    selected_radius
                )
                
                m = MapService.create_interactive_map(
                    st.session_state.selected_hawkercentre,
                    nearby,
                    location_details,
                    selected_radius,
                    self.df
                )
                st_folium(m, height=500, use_container_width=True)
            else:
                st.warning("Location coordinates not available for this hawker centre")
        
        with col2:
            self._display_centre_details(location_details)
    
    def _display_centre_details(self, location_details: LocationDetails) -> None:
        """Display detailed information about the selected centre."""
        # Selection section
        with st.container():
            st.markdown("##### 🎯 Your Selection")
            st.markdown(f"**Hawker Centre:**\n{st.session_state.selected_hawkercentre}")
            st.markdown(f"**Stall Type:**\n{st.session_state.selected_stalltype}")
            st.markdown(f" ")
        
        # Location section
        with st.container():
            st.markdown("##### 📍 Centre Address")
            st.markdown(f"{location_details.address} Singapore {location_details.postal_code}")
            st.markdown(f" ")
        
        # Stalls section
        with st.container():
            st.markdown("##### 🏪 Stall Count")
            # Get centre data
            centre_data = self.df[self.df['Hawker Centre'] == st.session_state.selected_hawkercentre].iloc[0]
            
            # Define stall types and their display names
            stall_types = {
                'Cooked Food': 'Cooked Food Stalls',
                'Locked-Up': 'Lock-up Stalls',
                'Market Slab': 'Market Slab Stalls',
                'Kiosks': 'Kiosks'
            }
            
            # Display counts for each stall type
            for col, display_name in stall_types.items():
                count = centre_data.get(col, 0)
                if pd.notna(count) and count > 0:
                    st.markdown(f"• **{display_name}**: {int(count)}")
    
    def _display_action_buttons(self) -> None:
        """Display main action buttons."""
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💬 Chat with HawkerGuru", use_container_width=True):
                st.session_state.chat_started = True
                st.session_state.calculator_started = False
        
        with col2:
            if st.button("🧮 Sustainable Bid Calculator", use_container_width=True):
                st.session_state.calculator_started = True
                st.session_state.chat_started = False

if __name__ == "__main__":
    if not check_password():
        st.stop()
    
    load_dotenv()
    app = HawkerGuruApp()
    app.run()