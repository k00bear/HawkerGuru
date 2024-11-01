"""
Data models for the HawkerGuru application.
This module contains dataclasses that define the structure of data objects used throughout the application.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class LocationDetails:
    """Details about a hawker centre location."""
    latitude: float
    longitude: float
    address: str
    postal_code: Optional[str] = None

@dataclass
class NearbyCenter:
    """Information about a nearby hawker centre."""
    name: str
    distance: float
    lat: float
    lon: float

@dataclass
class CalculationResults:
    """Results from financial calculations."""
    monthly_revenue: float
    monthly_costs: float
    sustainable_rent: float
    items_per_day: int
    avg_price: float
    days_per_month: int

@dataclass
class ChatMessage:
    """Structure for chat messages."""
    role: str
    content: str
    timestamp: Optional[str] = None

@dataclass
class StallDetails:
    """Details about a specific hawker stall."""
    hawker_centre: str
    stall_type: str
    stall_count: int
    landlord: str

@dataclass
class FinancialParameters:
    """Parameters for financial calculations."""
    class CostParameters:
        """Monthly operating cost parameters."""
        ingredients: float
        utilities: float
        sc_charges: float
        manpower: float
        cleaning: float
        misc_costs: float

    class RevenueParameters:
        """Revenue calculation parameters."""
        avg_price: float
        items_per_day: int
        days_per_month: int

    costs: CostParameters
    revenue: RevenueParameters