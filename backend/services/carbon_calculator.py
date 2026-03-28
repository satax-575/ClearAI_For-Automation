"""
Carbon Footprint Calculator
Implements GLEC Framework for logistics emissions
"""

from typing import Dict, Any
import math

class CarbonCalculator:
    def __init__(self):
        self.emission_factors = self._load_emission_factors()
        self.port_coordinates = self._load_port_coordinates()
    
    def calculate(
        self,
        origin_port: str,
        destination_port: str,
        weight_kg: float,
        transport_mode: str = "sea"
    ) -> Dict[str, Any]:
        """
        Calculate carbon footprint using GLEC Framework
        Formula: CO2e = Distance (km) × Weight (tons) × Emission Factor (g CO2/ton-km)
        """
        
        # Get distance
        distance_km = self._calculate_distance(origin_port, destination_port)
        
        # Convert weight to tons
        weight_tons = weight_kg / 1000
        
        # Get emission factor
        emission_factor = self.emission_factors.get(transport_mode, 10.5)
        
        # Calculate CO2 emissions (grams)
        co2_grams = distance_km * weight_tons * emission_factor
        
        # Convert to kg
        co2_kg = co2_grams / 1000
        
        # Calculate savings vs air freight
        air_emission_factor = self.emission_factors["air"]
        air_co2_kg = (distance_km * weight_tons * air_emission_factor) / 1000
        savings_kg = air_co2_kg - co2_kg
        
        return {
            "total_co2_kg": round(co2_kg, 2),
            "distance_km": distance_km,
            "weight_tons": weight_tons,
            "emission_factor": emission_factor,
            "transport_mode": transport_mode,
            "comparison": {
                "air_freight_co2_kg": round(air_co2_kg, 2),
                "savings_vs_air_kg": round(savings_kg, 2),
                "savings_percentage": round((savings_kg / air_co2_kg) * 100, 1) if air_co2_kg > 0 else 0
            },
            "equivalents": {
                "trees_to_offset": math.ceil(co2_kg / 21),  # 1 tree absorbs ~21kg CO2/year
                "car_km_equivalent": round(co2_kg / 0.12, 0),  # Average car: 120g CO2/km
                "days_of_electricity": round(co2_kg / 2.5, 1)  # Average home: 2.5kg CO2/day
            },
            "methodology": "GLEC Framework v2.0"
        }
    
    def _calculate_distance(self, origin: str, destination: str) -> float:
        """Calculate great circle distance between ports"""
        
        origin_coords = self.port_coordinates.get(origin)
        dest_coords = self.port_coordinates.get(destination)
        
        if not origin_coords or not dest_coords:
            # Default distance if ports not found
            return 2000.0
        
        # Haversine formula
        lat1, lon1 = math.radians(origin_coords[0]), math.radians(origin_coords[1])
        lat2, lon2 = math.radians(dest_coords[0]), math.radians(dest_coords[1])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Earth radius in km
        r = 6371
        
        return round(c * r, 2)
    
    def _load_emission_factors(self) -> Dict[str, float]:
        """
        Load GLEC emission factors (g CO2e per ton-km)
        Source: GLEC Framework v2.0
        """
        return {
            "sea": 10.5,      # Container ship
            "air": 602.0,     # Air cargo
            "road": 62.0,     # Truck
            "rail": 22.0,     # Rail freight
            "inland_water": 31.0  # Barge
        }
    
    def _load_port_coordinates(self) -> Dict[str, tuple]:
        """Load major port coordinates (lat, lon)"""
        return {
            # India
            "INMUN1": (18.9667, 72.8333),  # Mumbai/Nhava Sheva
            "INNSA1": (17.6833, 83.2167),  # Visakhapatnam
            "INCOK1": (9.9667, 76.2667),   # Cochin
            "INCHE1": (13.0833, 80.2833),  # Chennai
            
            # UAE
            "AEJEA": (25.0833, 55.1333),   # Jebel Ali, Dubai
            "AEAUH": (24.5333, 54.3833),   # Abu Dhabi
            
            # Singapore
            "SGSIN": (1.2667, 103.8),      # Singapore
            
            # USA
            "USLAX": (33.7333, -118.2667), # Los Angeles
            "USNYC": (40.6667, -74.0),     # New York
            
            # UK
            "GBFXT": (51.4333, 0.4333),    # Felixstowe
            "GBLGP": (53.4667, -3.0167),   # Liverpool
            
            # Germany
            "DEHAM": (53.55, 9.9833),      # Hamburg
            
            # China
            "CNSHA": (31.2, 121.5),        # Shanghai
            "CNSHK": (22.3, 114.1667),     # Shenzhen
            
            # Saudi Arabia
            "SAJED": (21.4833, 39.1833),   # Jeddah
        }
