"""
Document processing utilities
Handles document type detection and data merging
"""

from typing import Dict, Any, List, Optional
import re

class DocumentProcessor:
    def detect_document_type(self, content: bytes, filename: str) -> str:
        """
        Detect document type from content and filename
        """
        filename_lower = filename.lower()
        
        # Check filename patterns
        if any(x in filename_lower for x in ['invoice', 'inv', 'proforma']):
            return "invoice"
        elif any(x in filename_lower for x in ['packing', 'pack', 'pl']):
            return "packing_list"
        elif any(x in filename_lower for x in ['bill', 'lading', 'bl', 'bol']):
            return "bill_of_lading"
        elif any(x in filename_lower for x in ['certificate', 'origin', 'coo', 'cert']):
            return "certificate_of_origin"
        
        # Default to invoice
        return "invoice"
    
    def merge_document_data(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Merge data from multiple documents into single declaration
        Handles conflicts and validates consistency
        """
        merged = {
            "shipper": {},
            "consignee": {},
            "items": [],
            "total_value": 0,
            "currency": "USD",
            "origin_country": "IN",
            "destination_country": "AE",
            "total_weight": 0
        }
        
        for doc in documents:
            extracted = doc.get("extracted_data", {})
            doc_type = doc.get("document_type")
            
            # Merge shipper info (prefer invoice)
            if "shipper" in extracted and extracted["shipper"]:
                if not merged["shipper"] or doc_type == "invoice":
                    merged["shipper"].update(extracted["shipper"])
            
            # Merge consignee info
            if "consignee" in extracted and extracted["consignee"]:
                if not merged["consignee"] or doc_type == "invoice":
                    merged["consignee"].update(extracted["consignee"])
            
            # Merge items (prefer invoice for pricing, packing list for weight)
            if "items" in extracted:
                for item in extracted["items"]:
                    # Find matching item or add new
                    existing = self._find_matching_item(merged["items"], item)
                    if existing:
                        # Merge data
                        if doc_type == "invoice":
                            existing.update({
                                "unit_price": item.get("unit_price"),
                                "total_price": item.get("total_price")
                            })
                        elif doc_type == "packing_list":
                            existing.update({
                                "gross_weight_kg": item.get("gross_weight_kg"),
                                "net_weight_kg": item.get("net_weight_kg"),
                                "package_type": item.get("package_type")
                            })
                    else:
                        merged["items"].append(item)
            
            # Merge totals
            if "total_value" in extracted:
                merged["total_value"] = max(merged["total_value"], extracted["total_value"])
            
            if "currency" in extracted:
                merged["currency"] = extracted["currency"]
            
            # Merge origin/destination
            if doc_type == "certificate_of_origin":
                if "origin_country" in extracted:
                    merged["origin_country"] = extracted["origin_country"]
                if "destination_country" in extracted:
                    merged["destination_country"] = extracted["destination_country"]
            
            # Merge ports (from bill of lading)
            if doc_type == "bill_of_lading":
                if "port_of_loading" in extracted:
                    merged["origin_port"] = self._normalize_port_code(extracted["port_of_loading"])
                if "port_of_discharge" in extracted:
                    merged["destination_port"] = self._normalize_port_code(extracted["port_of_discharge"])
        
        # Calculate total weight
        merged["total_weight"] = sum(
            item.get("weight_kg", 0) or item.get("net_weight_kg", 0) 
            for item in merged["items"]
        )
        
        return merged
    
    def _find_matching_item(
        self, 
        items: List[Dict[str, Any]], 
        new_item: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Find matching item in list by description similarity"""
        new_desc = new_item.get("description", "").lower()
        
        for item in items:
            existing_desc = item.get("description", "").lower()
            
            # Simple similarity check
            if self._similarity(new_desc, existing_desc) > 0.8:
                return item
        
        return None
    
    def _similarity(self, s1: str, s2: str) -> float:
        """Calculate string similarity (0-1)"""
        if not s1 or not s2:
            return 0.0
        
        # Simple word overlap
        words1 = set(s1.split())
        words2 = set(s2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def _normalize_port_code(self, port_name: str) -> str:
        """Convert port name to UN/LOCODE"""
        port_map = {
            "mumbai": "INMUN1",
            "nhava sheva": "INMUN1",
            "jnpt": "INMUN1",
            "dubai": "AEJEA",
            "jebel ali": "AEJEA",
            "abu dhabi": "AEAUH",
            "singapore": "SGSIN",
            "chennai": "INCHE1",
            "cochin": "INCOK1",
            "visakhapatnam": "INNSA1"
        }
        return port_map.get(port_name.lower(), port_name.upper())


from typing import Optional
