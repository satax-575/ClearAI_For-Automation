"""
AI-powered document data extraction service
Uses GPT-4 Vision for OCR and structured data extraction
"""

import os
import base64
import json
from typing import Dict, Any, Optional
import anthropic
from openai import OpenAI

class AIExtractor:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.use_claude = os.getenv("USE_CLAUDE", "true").lower() == "true"
    
    def check_health(self) -> bool:
        """Check if AI service is available"""
        return bool(os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY"))
    
    async def extract_from_document(
        self, 
        content: bytes, 
        filename: str, 
        document_type: str
    ) -> Dict[str, Any]:
        """
        Extract structured data from document using AI vision models
        """
        # Convert to base64
        base64_content = base64.b64encode(content).decode('utf-8')
        
        # Get extraction prompt based on document type
        prompt = self._get_extraction_prompt(document_type)
        
        # Use Claude or GPT-4V
        if self.use_claude and self.anthropic_client:
            extracted = await self._extract_with_claude(base64_content, prompt, filename)
        else:
            extracted = await self._extract_with_gpt4v(base64_content, prompt, filename)
        
        # Post-process and validate
        extracted = self._post_process(extracted, document_type)
        
        return extracted
    
    async def _extract_with_claude(
        self, 
        base64_content: str, 
        prompt: str, 
        filename: str
    ) -> Dict[str, Any]:
        """Extract using Claude 3.5 Sonnet with vision"""
        try:
            # Determine media type
            media_type = "image/jpeg" if filename.lower().endswith(('.jpg', '.jpeg')) else "image/png"
            if filename.lower().endswith('.pdf'):
                media_type = "application/pdf"
            
            message = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": base64_content,
                                },
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ],
                    }
                ],
            )
            
            # Parse JSON response
            response_text = message.content[0].text
            
            # Extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
            
            return {"error": "Failed to parse AI response", "raw": response_text}
            
        except Exception as e:
            return {"error": f"Claude extraction failed: {str(e)}"}
    
    async def _extract_with_gpt4v(
        self, 
        base64_content: str, 
        prompt: str, 
        filename: str
    ) -> Dict[str, Any]:
        """Extract using GPT-4 Vision"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_content}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=4096
            )
            
            response_text = response.choices[0].message.content
            
            # Extract JSON
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
            
            return {"error": "Failed to parse AI response", "raw": response_text}
            
        except Exception as e:
            return {"error": f"GPT-4V extraction failed: {str(e)}"}
    
    def _get_extraction_prompt(self, document_type: str) -> str:
        """Get extraction prompt template for document type"""
        
        prompts = {
            "invoice": """
Extract all data from this commercial invoice and return as JSON:
{
  "invoice_number": "string",
  "invoice_date": "YYYY-MM-DD",
  "shipper": {
    "name": "string",
    "address": "string",
    "country": "string",
    "tax_id": "string"
  },
  "consignee": {
    "name": "string",
    "address": "string",
    "country": "string",
    "tax_id": "string"
  },
  "items": [
    {
      "description": "string",
      "quantity": number,
      "unit": "string",
      "unit_price": number,
      "total_price": number,
      "weight_kg": number
    }
  ],
  "total_value": number,
  "currency": "string",
  "payment_terms": "string",
  "confidence": 0.95
}
Extract all visible text accurately. If a field is not found, use null.
""",
            "packing_list": """
Extract all data from this packing list and return as JSON:
{
  "packing_list_number": "string",
  "date": "YYYY-MM-DD",
  "shipper": {"name": "string", "address": "string"},
  "consignee": {"name": "string", "address": "string"},
  "items": [
    {
      "description": "string",
      "quantity": number,
      "unit": "string",
      "gross_weight_kg": number,
      "net_weight_kg": number,
      "dimensions": "string",
      "package_type": "string",
      "marks_numbers": "string"
    }
  ],
  "total_packages": number,
  "total_gross_weight_kg": number,
  "total_net_weight_kg": number,
  "confidence": 0.95
}
""",
            "bill_of_lading": """
Extract all data from this bill of lading and return as JSON:
{
  "bl_number": "string",
  "date": "YYYY-MM-DD",
  "shipper": {"name": "string", "address": "string"},
  "consignee": {"name": "string", "address": "string"},
  "notify_party": {"name": "string", "address": "string"},
  "vessel": "string",
  "voyage": "string",
  "port_of_loading": "string",
  "port_of_discharge": "string",
  "place_of_delivery": "string",
  "container_numbers": ["string"],
  "seal_numbers": ["string"],
  "freight_terms": "string",
  "number_of_originals": number,
  "confidence": 0.95
}
""",
            "certificate_of_origin": """
Extract all data from this certificate of origin and return as JSON:
{
  "certificate_number": "string",
  "issue_date": "YYYY-MM-DD",
  "expiry_date": "YYYY-MM-DD",
  "exporter": {"name": "string", "address": "string", "country": "string"},
  "consignee": {"name": "string", "address": "string", "country": "string"},
  "origin_country": "string",
  "destination_country": "string",
  "items": [
    {
      "description": "string",
      "hs_code": "string",
      "quantity": number,
      "origin_criteria": "string"
    }
  ],
  "issuing_authority": "string",
  "fta_reference": "string",
  "confidence": 0.95
}
"""
        }
        
        return prompts.get(document_type, prompts["invoice"])
    
    def _post_process(self, data: Dict[str, Any], document_type: str) -> Dict[str, Any]:
        """Clean and validate extracted data"""
        # Add document type
        data["document_type"] = document_type
        
        # Ensure confidence score
        if "confidence" not in data:
            data["confidence"] = 0.85
        
        # Normalize country codes
        if "shipper" in data and "country" in data["shipper"]:
            data["shipper"]["country"] = self._normalize_country_code(data["shipper"]["country"])
        
        if "consignee" in data and "country" in data["consignee"]:
            data["consignee"]["country"] = self._normalize_country_code(data["consignee"]["country"])
        
        return data
    
    def _normalize_country_code(self, country: str) -> str:
        """Convert country name to ISO 2-letter code"""
        country_map = {
            "india": "IN",
            "united arab emirates": "AE",
            "uae": "AE",
            "dubai": "AE",
            "usa": "US",
            "united states": "US",
            "uk": "GB",
            "united kingdom": "GB",
            "singapore": "SG",
            "china": "CN",
            "germany": "DE"
        }
        return country_map.get(country.lower(), country.upper()[:2])
