"""
HS Code Classification Service
Classifies product descriptions to Harmonized System codes
"""

import re
from typing import Dict, Any, Optional
import anthropic
import os

class HSCodeClassifier:
    def __init__(self):
        self.hs_database = self._load_hs_database()
        self.anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    def check_health(self) -> bool:
        return len(self.hs_database) > 0
    
    def classify(self, description: str, category: Optional[str] = None) -> Dict[str, Any]:
        """
        Classify product description to HS code
        Uses hybrid approach: rule-based + AI
        """
        # Clean description
        description = description.strip().lower()
        
        # Try rule-based first (fast)
        rule_based = self._rule_based_classification(description)
        if rule_based["confidence"] > 0.9:
            return rule_based
        
        # Fall back to AI classification
        ai_based = self._ai_classification(description, category)
        
        # Return higher confidence result
        if ai_based["confidence"] > rule_based["confidence"]:
            return ai_based
        return rule_based
    
    def _rule_based_classification(self, description: str) -> Dict[str, Any]:
        """Fast rule-based classification using keyword matching"""
        
        # Search HS database
        best_match = None
        best_score = 0
        
        for hs_code, data in self.hs_database.items():
            keywords = data["keywords"]
            score = sum(1 for kw in keywords if kw in description)
            
            if score > best_score:
                best_score = score
                best_match = (hs_code, data)
        
        if best_match:
            hs_code, data = best_match
            confidence = min(0.95, 0.6 + (best_score * 0.1))
            
            return {
                "code": hs_code,
                "description": data["description"],
                "confidence": confidence,
                "method": "rule_based",
                "chapter": hs_code[:2],
                "heading": hs_code[:4]
            }
        
        return {
            "code": "0000.00.00",
            "description": "Unknown",
            "confidence": 0.0,
            "method": "rule_based"
        }
    
    def _ai_classification(self, description: str, category: Optional[str] = None) -> Dict[str, Any]:
        """AI-powered classification using Claude"""
        try:
            prompt = f"""
Classify this product to its correct HS (Harmonized System) code:

Product: {description}
{f"Category: {category}" if category else ""}

Provide the 6-digit HS code and explanation. Use this format:
{{
  "code": "XXXX.XX",
  "description": "Official HS description",
  "confidence": 0.95,
  "reasoning": "Why this code was chosen"
}}

Common HS chapters:
- 84: Machinery, mechanical appliances
- 85: Electrical machinery and equipment
- 62/63: Textiles and clothing
- 09: Coffee, tea, spices
- 10: Cereals
- 39: Plastics
- 73: Iron and steel articles
"""
            
            message = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text
            
            # Parse JSON
            import json
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start >= 0:
                result = json.loads(response_text[json_start:json_end])
                result["method"] = "ai_powered"
                result["chapter"] = result["code"][:2]
                result["heading"] = result["code"][:4]
                return result
            
        except Exception as e:
            print(f"AI classification failed: {e}")
        
        # Fallback
        return {
            "code": "0000.00.00",
            "description": "Classification failed",
            "confidence": 0.0,
            "method": "failed"
        }
    
    def _load_hs_database(self) -> Dict[str, Dict[str, Any]]:
        """Load HS code database with keywords"""
        return {
            "8471.30": {
                "description": "Portable automatic data processing machines, weighing not more than 10 kg (laptops)",
                "keywords": ["laptop", "notebook", "portable computer", "macbook"]
            },
            "8471.41": {
                "description": "Data processing machines (computers)",
                "keywords": ["computer", "desktop", "pc", "workstation"]
            },
            "8517.12": {
                "description": "Telephones for cellular networks (smartphones)",
                "keywords": ["smartphone", "mobile phone", "iphone", "android phone"]
            },
            "8517.62": {
                "description": "Machines for reception, conversion and transmission of data",
                "keywords": ["router", "modem", "network equipment"]
            },
            "6203.42": {
                "description": "Men's or boys' trousers of cotton",
                "keywords": ["trousers", "pants", "jeans", "cotton pants"]
            },
            "6204.62": {
                "description": "Women's or girls' trousers of cotton",
                "keywords": ["women trousers", "ladies pants", "women jeans"]
            },
            "0901.21": {
                "description": "Coffee, roasted, not decaffeinated",
                "keywords": ["coffee", "roasted coffee", "coffee beans"]
            },
            "0902.30": {
                "description": "Black tea (fermented)",
                "keywords": ["black tea", "tea", "fermented tea"]
            },
            "1006.30": {
                "description": "Semi-milled or wholly milled rice",
                "keywords": ["rice", "basmati", "milled rice"]
            },
            "0908.11": {
                "description": "Nutmeg",
                "keywords": ["nutmeg", "jaiphal"]
            },
            "0908.31": {
                "description": "Cardamom",
                "keywords": ["cardamom", "elaichi"]
            },
            "0904.21": {
                "description": "Dried chillies",
                "keywords": ["chilli", "red chilli", "dried chilli"]
            },
            "3926.90": {
                "description": "Other articles of plastics",
                "keywords": ["plastic", "plastic products", "plastic items"]
            },
            "7323.93": {
                "description": "Stainless steel tableware",
                "keywords": ["steel utensils", "stainless steel", "cutlery"]
            },
            "9403.60": {
                "description": "Wooden furniture",
                "keywords": ["wooden furniture", "wood furniture", "furniture"]
            },
            "6302.60": {
                "description": "Toilet linen and kitchen linen of terry towelling",
                "keywords": ["towels", "bath towels", "terry towel"]
            },
            "7113.19": {
                "description": "Jewellery of precious metal",
                "keywords": ["jewellery", "jewelry", "gold jewellery", "silver jewellery"]
            },
            "8528.72": {
                "description": "Reception apparatus for television",
                "keywords": ["television", "tv", "led tv", "smart tv"]
            },
            "8414.51": {
                "description": "Table, floor, wall, window fans",
                "keywords": ["fan", "table fan", "ceiling fan"]
            },
            "8516.60": {
                "description": "Electric ovens; cookers, cooking plates",
                "keywords": ["oven", "microwave", "cooking range"]
            }
        }
    
    def _check_fta_eligibility(self, origin: str, destination: str) -> bool:
        """Check FTA eligibility"""
        fta_pairs = [
            ("IN", "AE"),
            ("IN", "SG"),
            ("IN", "JP"),
            ("IN", "KR")
        ]
        return (origin, destination) in fta_pairs
