"""
Compliance validation engine
Validates customs declarations against trade regulations
"""

import json
from typing import Dict, Any, List
from datetime import datetime, timedelta

class ComplianceEngine:
    def __init__(self):
        self.regulations = self._load_regulations()
        self.fta_rules = self._load_fta_rules()
    
    def check_health(self) -> bool:
        return len(self.regulations) > 0
    
    def validate(
        self, 
        declaration: Dict[str, Any], 
        origin: str = "IN", 
        destination: str = "AE"
    ) -> Dict[str, Any]:
        """
        Validate declaration against compliance rules
        Returns errors, warnings, and compliance score
        """
        errors = []
        warnings = []
        
        # Check required fields
        required_fields = [
            "shipper", "consignee", "items", "total_value", 
            "currency", "origin_country", "destination_country"
        ]
        for field in required_fields:
            if field not in declaration or not declaration[field]:
                errors.append({
                    "field": field,
                    "message": f"Required field '{field}' is missing",
                    "severity": "error"
                })
        
        # Validate items
        if "items" in declaration:
            for idx, item in enumerate(declaration["items"]):
                item_errors = self._validate_item(item, idx, origin, destination)
                errors.extend(item_errors)
        
        # Check prohibited goods
        prohibited = self._check_prohibited_goods(declaration, destination)
        errors.extend(prohibited)
        
        # Check value limits
        value_check = self._check_value_limits(declaration, destination)
        warnings.extend(value_check)
        
        # Check document consistency
        consistency = self._check_document_consistency(declaration)
        errors.extend(consistency["errors"])
        warnings.extend(consistency["warnings"])
        
        # Calculate compliance score
        total_checks = 47  # Total number of validation rules
        failed_checks = len(errors)
        compliance_score = max(0, (total_checks - failed_checks) / total_checks)
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "compliance_score": round(compliance_score, 2),
            "recommendations": self._generate_recommendations(errors, warnings)
        }
    
    def calculate_duties(
        self, 
        items: List[Dict[str, Any]], 
        origin: str = "IN", 
        destination: str = "AE"
    ) -> Dict[str, Any]:
        """Calculate customs duties and taxes"""
        
        total_duty = 0
        fta_eligible = self._check_fta_eligibility(origin, destination)
        
        duty_breakdown = []
        
        for item in items:
            hs_code = item.get("hs_code", "")
            value = item.get("total_price", 0)
            
            # Get duty rate
            duty_rate = self._get_duty_rate(hs_code, origin, destination, fta_eligible)
            
            # Calculate duty
            duty_amount = value * duty_rate
            total_duty += duty_amount
            
            duty_breakdown.append({
                "description": item.get("description"),
                "hs_code": hs_code,
                "value": value,
                "duty_rate": duty_rate,
                "duty_amount": round(duty_amount, 2)
            })
        
        return {
            "total_duty": round(total_duty, 2),
            "fta_eligible": fta_eligible,
            "fta_name": "India-UAE CEPA" if fta_eligible else None,
            "duty_breakdown": duty_breakdown
        }
    
    def get_country_regulations(self, country_code: str) -> Optional[Dict[str, Any]]:
        """Get regulations for specific country"""
        return self.regulations.get(country_code)
    
    def _validate_item(
        self, 
        item: Dict[str, Any], 
        index: int, 
        origin: str, 
        destination: str
    ) -> List[Dict[str, str]]:
        """Validate individual item"""
        errors = []
        
        # Check required item fields
        required = ["description", "quantity", "unit_price"]
        for field in required:
            if field not in item or item[field] is None:
                errors.append({
                    "field": f"items[{index}].{field}",
                    "message": f"Item {index + 1}: Missing {field}",
                    "severity": "error"
                })
        
        # Validate HS code format
        if "hs_code" in item:
            hs_code = str(item["hs_code"])
            if not hs_code.isdigit() or len(hs_code) not in [6, 8, 10]:
                errors.append({
                    "field": f"items[{index}].hs_code",
                    "message": f"Item {index + 1}: Invalid HS code format (must be 6, 8, or 10 digits)",
                    "severity": "error"
                })
        
        # Validate quantities
        if "quantity" in item and item["quantity"] <= 0:
            errors.append({
                "field": f"items[{index}].quantity",
                "message": f"Item {index + 1}: Quantity must be positive",
                "severity": "error"
            })
        
        return errors
    
    def _check_prohibited_goods(
        self, 
        declaration: Dict[str, Any], 
        destination: str
    ) -> List[Dict[str, str]]:
        """Check for prohibited goods"""
        errors = []
        
        prohibited_keywords = {
            "AE": ["alcohol", "pork", "gambling", "narcotics", "weapons"],
            "IN": ["beef", "narcotics", "weapons", "endangered species"]
        }
        
        keywords = prohibited_keywords.get(destination, [])
        
        for idx, item in enumerate(declaration.get("items", [])):
            desc = item.get("description", "").lower()
            for keyword in keywords:
                if keyword in desc:
                    errors.append({
                        "field": f"items[{idx}].description",
                        "message": f"Item {idx + 1}: May contain prohibited goods ({keyword})",
                        "severity": "error"
                    })
        
        return errors
    
    def _check_value_limits(
        self, 
        declaration: Dict[str, Any], 
        destination: str
    ) -> List[Dict[str, str]]:
        """Check value thresholds"""
        warnings = []
        
        total_value = declaration.get("total_value", 0)
        
        # High value shipment warning
        if total_value > 100000:
            warnings.append({
                "field": "total_value",
                "message": "High value shipment (>$100K) may require additional documentation",
                "severity": "warning"
            })
        
        return warnings
    
    def _check_document_consistency(
        self, 
        declaration: Dict[str, Any]
    ) -> Dict[str, List]:
        """Check consistency across documents"""
        errors = []
        warnings = []
        
        # Check shipper/consignee consistency
        # (In real implementation, compare across multiple uploaded documents)
        
        # Check weight consistency
        invoice_weight = sum(item.get("weight_kg", 0) for item in declaration.get("items", []))
        declared_weight = declaration.get("total_weight", invoice_weight)
        
        if abs(invoice_weight - declared_weight) > declared_weight * 0.05:  # 5% tolerance
            warnings.append({
                "field": "total_weight",
                "message": f"Weight mismatch: Invoice shows {invoice_weight}kg, declared {declared_weight}kg",
                "severity": "warning"
            })
        
        return {"errors": errors, "warnings": warnings}
    
    def _check_fta_eligibility(self, origin: str, destination: str) -> bool:
        """Check if shipment qualifies for FTA benefits"""
        fta_pairs = [
            ("IN", "AE"),  # India-UAE CEPA
            ("IN", "SG"),  # India-Singapore CECA
            ("IN", "JP"),  # India-Japan CEPA
        ]
        return (origin, destination) in fta_pairs or (destination, origin) in fta_pairs
    
    def _get_duty_rate(
        self, 
        hs_code: str, 
        origin: str, 
        destination: str, 
        fta_eligible: bool
    ) -> float:
        """Get applicable duty rate for HS code"""
        
        # Simplified duty rates (real implementation would query customs DB)
        if fta_eligible and origin == "IN" and destination == "AE":
            return 0.0  # India-UAE CEPA: 0% on most goods
        
        # Default MFN rates for UAE
        if destination == "AE":
            hs_prefix = hs_code[:4]
            duty_rates = {
                "8471": 0.05,  # Computers: 5%
                "8517": 0.05,  # Telecom equipment: 5%
                "6203": 0.05,  # Garments: 5%
                "0901": 0.0,   # Coffee: 0%
                "1006": 0.0,   # Rice: 0%
            }
            return duty_rates.get(hs_prefix, 0.05)  # Default 5%
        
        return 0.1  # Default 10%
    
    def _generate_recommendations(
        self, 
        errors: List[Dict], 
        warnings: List[Dict]
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if errors:
            recommendations.append("Fix all errors before submitting to customs")
        
        if warnings:
            recommendations.append("Review warnings to avoid potential delays")
        
        if not errors and not warnings:
            recommendations.append("Declaration is ready for submission")
        
        return recommendations
    
    def _load_regulations(self) -> Dict[str, Any]:
        """Load customs regulations database"""
        # Simplified - real implementation would load from database
        return {
            "IN": {
                "country_name": "India",
                "customs_authority": "CBIC",
                "prohibited_imports": ["beef", "narcotics", "weapons"],
                "restricted_imports": ["gold", "silver", "electronics"],
                "documentation_required": [
                    "Commercial Invoice",
                    "Packing List",
                    "Bill of Lading",
                    "Certificate of Origin"
                ]
            },
            "AE": {
                "country_name": "United Arab Emirates",
                "customs_authority": "Federal Customs Authority",
                "prohibited_imports": ["alcohol", "pork", "gambling", "narcotics"],
                "restricted_imports": ["pharmaceuticals", "chemicals"],
                "documentation_required": [
                    "Commercial Invoice",
                    "Packing List",
                    "Bill of Lading",
                    "Certificate of Origin"
                ]
            }
        }
    
    def _load_fta_rules(self) -> Dict[str, Any]:
        """Load FTA rules database"""
        return {
            "IN-AE": {
                "name": "India-UAE Comprehensive Economic Partnership Agreement (CEPA)",
                "effective_date": "2022-05-01",
                "tariff_elimination": 0.9,  # 90% of tariff lines
                "origin_rules": "Regional Value Content >= 40%",
                "documentation": ["Certificate of Origin Form CEPA"]
            }
        }
