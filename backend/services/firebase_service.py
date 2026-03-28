"""
Firebase integration service
Handles Firestore database and Storage operations
"""

import os
import json
from typing import Dict, Any, Optional
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore, storage
from google.cloud.firestore_v1.base_query import FieldFilter

class FirebaseService:
    def __init__(self):
        # Initialize Firebase Admin SDK
        if not firebase_admin._apps:
            cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase-credentials.json")
            if os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred, {
                    'storageBucket': os.getenv("FIREBASE_STORAGE_BUCKET", "clearpath-customs.appspot.com")
                })
            else:
                # Use default credentials in Cloud Run
                firebase_admin.initialize_app()
        
        self.db = firestore.client()
        self.bucket = storage.bucket()
    
    def check_health(self) -> bool:
        """Check Firebase connection"""
        try:
            # Try to read from Firestore
            self.db.collection('_health').limit(1).get()
            return True
        except:
            return False
    
    async def upload_document(
        self, 
        doc_id: str, 
        content: bytes, 
        filename: str, 
        user_id: str
    ) -> str:
        """Upload document to Firebase Storage"""
        try:
            # Create blob path
            blob_path = f"documents/{user_id}/{doc_id}/{filename}"
            blob = self.bucket.blob(blob_path)
            
            # Upload with metadata
            blob.upload_from_string(
                content,
                content_type=self._get_content_type(filename)
            )
            
            # Make publicly accessible (configure for production)
            blob.make_public()
            
            return blob.public_url
            
        except Exception as e:
            raise Exception(f"Firebase upload failed: {str(e)}")
    
    async def save_document_metadata(
        self, 
        doc_id: str, 
        metadata: Dict[str, Any]
    ) -> None:
        """Save document metadata to Firestore"""
        try:
            self.db.collection('documents').document(doc_id).set(metadata)
        except Exception as e:
            raise Exception(f"Firestore save failed: {str(e)}")
    
    async def get_document_metadata(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve document metadata"""
        try:
            doc = self.db.collection('documents').document(doc_id).get()
            return doc.to_dict() if doc.exists else None
        except Exception as e:
            raise Exception(f"Firestore read failed: {str(e)}")
    
    async def save_declaration(
        self, 
        declaration_id: str, 
        declaration: Dict[str, Any]
    ) -> None:
        """Save customs declaration"""
        try:
            self.db.collection('declarations').document(declaration_id).set(declaration)
        except Exception as e:
            raise Exception(f"Declaration save failed: {str(e)}")
    
    async def get_declaration(self, declaration_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve customs declaration"""
        try:
            doc = self.db.collection('declarations').document(declaration_id).get()
            return doc.to_dict() if doc.exists else None
        except Exception as e:
            raise Exception(f"Declaration read failed: {str(e)}")
    
    async def get_user_declarations(
        self, 
        user_id: str, 
        limit: int = 50
    ) -> list:
        """Get all declarations for a user"""
        try:
            docs = (
                self.db.collection('declarations')
                .where(filter=FieldFilter('user_id', '==', user_id))
                .order_by('created_at', direction=firestore.Query.DESCENDING)
                .limit(limit)
                .stream()
            )
            return [doc.to_dict() for doc in docs]
        except Exception as e:
            raise Exception(f"Query failed: {str(e)}")
    
    async def get_user_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get analytics for user dashboard"""
        try:
            declarations = await self.get_user_declarations(user_id, limit=1000)
            
            total_shipments = len(declarations)
            total_value = sum(d.get("total_value", 0) for d in declarations)
            total_carbon = sum(d.get("carbon_footprint", 0) for d in declarations)
            total_duty_saved = sum(
                d.get("duty_amount", 0) 
                for d in declarations 
                if d.get("fta_eligible", False)
            )
            
            # Calculate average processing time
            avg_processing_time = 2.5  # hours (placeholder)
            
            return {
                "total_shipments": total_shipments,
                "total_value_usd": round(total_value, 2),
                "total_carbon_kg": round(total_carbon, 2),
                "total_duty_saved_usd": round(total_duty_saved, 2),
                "avg_processing_time_hours": avg_processing_time,
                "time_saved_days": round(total_shipments * 5, 1),  # 5 days saved per shipment
                "cost_saved_usd": round(total_shipments * 10000, 2),  # ₹10K saved per shipment
                "trees_equivalent": math.ceil(total_carbon / 21)
            }
        except Exception as e:
            return {
                "error": str(e),
                "total_shipments": 0
            }
    
    def _get_content_type(self, filename: str) -> str:
        """Determine content type from filename"""
        ext = filename.lower().split('.')[-1]
        content_types = {
            'pdf': 'application/pdf',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'xls': 'application/vnd.ms-excel'
        }
        return content_types.get(ext, 'application/octet-stream')


import math
