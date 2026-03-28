"""
ClearPath Customs Pre-Clearance Agent - Main API
FastAPI backend for AI-powered customs document processing
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import os
from datetime import datetime
import uuid

from services.document_processor import DocumentProcessor
from services.ai_extractor import AIExtractor
from services.compliance_engine import ComplianceEngine
from services.hs_classifier import HSCodeClassifier
from services.carbon_calculator import CarbonCalculator
from services.firebase_service import FirebaseService
from utils.logger import setup_logger

# Initialize FastAPI app
app = FastAPI(
    title="ClearPath API",
    description="AI-Powered Customs Pre-Clearance for SME Exporters",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
logger = setup_logger(__name__)
doc_processor = DocumentProcessor()
ai_extractor = AIExtractor()
compliance_engine = ComplianceEngine()
hs_classifier = HSCodeClassifier()
carbon_calculator = CarbonCalculator()
firebase_service = FirebaseService()


# Pydantic Models
class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    document_type: str
    extracted_data: Dict[str, Any]
    confidence_score: float
    processing_time_ms: int


class CustomsDeclaration(BaseModel):
    declaration_id: str
    shipper: Dict[str, str]
    consignee: Dict[str, str]
    items: List[Dict[str, Any]]
    total_value: float
    currency: str
    origin_country: str
    destination_country: str
    hs_codes: List[str]
    duty_amount: float
    fta_eligible: bool
    carbon_footprint: float
    status: str
    errors: List[str] = []
    warnings: List[str] = []
    created_at: datetime


class ValidationResult(BaseModel):
    is_valid: bool
    errors: List[Dict[str, str]]
    warnings: List[Dict[str, str]]
    compliance_score: float
    recommendations: List[str]


# Health check endpoint
@app.get("/")
async def root():
    return {
        "service": "ClearPath API",
        "status": "operational",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "services": {
            "ai_extractor": ai_extractor.check_health(),
            "compliance_engine": compliance_engine.check_health(),
            "firebase": firebase_service.check_health(),
            "hs_classifier": hs_classifier.check_health()
        }
    }


# Document upload and processing
@app.post("/api/v1/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    document_type: Optional[str] = None,
    user_id: str = "demo_user"
):
    """
    Upload and process a customs document
    Supported types: invoice, packing_list, bill_of_lading, certificate_of_origin
    """
    try:
        start_time = datetime.utcnow()
        
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Read file content
        content = await file.read()
        
        # Process document
        doc_id = str(uuid.uuid4())
        
        # Detect document type if not provided
        if not document_type:
            document_type = doc_processor.detect_document_type(content, file.filename)
        
        # Extract data using AI
        extracted_data = await ai_extractor.extract_from_document(
            content, 
            file.filename, 
            document_type
        )
        
        # Store in Firebase
        storage_url = firebase_service.upload_document(
            doc_id, 
            content, 
            file.filename, 
            user_id
        )
        
        # Save metadata
        firebase_service.save_document_metadata(
            doc_id,
            {
                "filename": file.filename,
                "document_type": document_type,
                "extracted_data": extracted_data,
                "storage_url": storage_url,
                "user_id": user_id,
                "uploaded_at": datetime.utcnow().isoformat()
            }
        )
        
        processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        logger.info(f"Document processed: {doc_id} in {processing_time}ms")
        
        return DocumentUploadResponse(
            document_id=doc_id,
            filename=file.filename,
            document_type=document_type,
            extracted_data=extracted_data,
            confidence_score=extracted_data.get("confidence", 0.95),
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        logger.error(f"Document upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@app.post("/api/v1/declarations/generate")
async def generate_declaration(
    document_ids: List[str],
    user_id: str = "demo_user"
):
    """
    Generate customs declaration from uploaded documents
    Requires: invoice, packing_list, bill_of_lading (minimum)
    """
    try:
        # Retrieve documents
        documents = []
        for doc_id in document_ids:
            doc = firebase_service.get_document_metadata(doc_id)
            if not doc:
                raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")
            documents.append(doc)
        
        # Validate required documents
        doc_types = [d["document_type"] for d in documents]
        required = ["invoice", "packing_list"]
        missing = [t for t in required if t not in doc_types]
        if missing:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required documents: {', '.join(missing)}"
            )
        
        # Merge extracted data
        merged_data = doc_processor.merge_document_data(documents)
        
        # Classify HS codes
        items_with_hs = []
        for item in merged_data.get("items", []):
            hs_code = hs_classifier.classify(item["description"])
            item["hs_code"] = hs_code["code"]
            item["hs_confidence"] = hs_code["confidence"]
            items_with_hs.append(item)
        
        # Run compliance checks
        validation = compliance_engine.validate(
            merged_data,
            origin=merged_data.get("origin_country", "IN"),
            destination=merged_data.get("destination_country", "AE")
        )
        
        # Calculate duties
        duty_info = compliance_engine.calculate_duties(
            items_with_hs,
            origin=merged_data.get("origin_country", "IN"),
            destination=merged_data.get("destination_country", "AE")
        )
        
        # Calculate carbon footprint
        carbon = carbon_calculator.calculate(
            origin_port=merged_data.get("origin_port", "INMUN1"),
            destination_port=merged_data.get("destination_port", "AEJEA"),
            weight_kg=merged_data.get("total_weight", 1000),
            transport_mode="sea"
        )
        
        # Generate declaration
        declaration_id = f"CLRP-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        declaration = {
            "declaration_id": declaration_id,
            "shipper": merged_data.get("shipper", {}),
            "consignee": merged_data.get("consignee", {}),
            "items": items_with_hs,
            "total_value": merged_data.get("total_value", 0),
            "currency": merged_data.get("currency", "USD"),
            "origin_country": merged_data.get("origin_country", "IN"),
            "destination_country": merged_data.get("destination_country", "AE"),
            "hs_codes": [item["hs_code"] for item in items_with_hs],
            "duty_amount": duty_info["total_duty"],
            "fta_eligible": duty_info["fta_eligible"],
            "carbon_footprint": carbon["total_co2_kg"],
            "status": "READY_TO_SUBMIT" if validation["is_valid"] else "REQUIRES_REVIEW",
            "errors": validation["errors"],
            "warnings": validation["warnings"],
            "created_at": datetime.utcnow().isoformat(),
            "user_id": user_id
        }
        
        # Save declaration
        firebase_service.save_declaration(declaration_id, declaration)
        
        logger.info(f"Declaration generated: {declaration_id}")
        
        return declaration
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Declaration generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@app.get("/api/v1/declarations/{declaration_id}")
async def get_declaration(declaration_id: str):
    """Retrieve a customs declaration by ID"""
    try:
        declaration = firebase_service.get_declaration(declaration_id)
        if not declaration:
            raise HTTPException(status_code=404, detail="Declaration not found")
        return declaration
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve declaration: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/validate")
async def validate_declaration(declaration: Dict[str, Any]):
    """
    Validate a customs declaration against compliance rules
    Returns errors, warnings, and compliance score
    """
    try:
        result = compliance_engine.validate(
            declaration,
            origin=declaration.get("origin_country", "IN"),
            destination=declaration.get("destination_country", "AE")
        )
        return result
    except Exception as e:
        logger.error(f"Validation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/hs-code/classify")
async def classify_hs_code(description: str, category: Optional[str] = None):
    """
    Classify product description to HS code
    Uses AI + rule-based hybrid approach
    """
    try:
        result = hs_classifier.classify(description, category)
        return result
    except Exception as e:
        logger.error(f"HS classification failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/carbon/calculate")
async def calculate_carbon(
    origin_port: str,
    destination_port: str,
    weight_kg: float,
    transport_mode: str = "sea"
):
    """
    Calculate carbon footprint for shipment
    Uses GLEC Framework methodology
    """
    try:
        result = carbon_calculator.calculate(
            origin_port, destination_port, weight_kg, transport_mode
        )
        return result
    except Exception as e:
        logger.error(f"Carbon calculation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/regulations/{country_code}")
async def get_regulations(country_code: str):
    """Get customs regulations for a specific country"""
    try:
        regulations = compliance_engine.get_country_regulations(country_code)
        if not regulations:
            raise HTTPException(status_code=404, detail=f"Regulations for {country_code} not found")
        return regulations
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve regulations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/analytics/dashboard")
async def get_analytics(user_id: str):
    """Get user analytics dashboard data"""
    try:
        analytics = firebase_service.get_user_analytics(user_id)
        return analytics
    except Exception as e:
        logger.error(f"Analytics retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )
