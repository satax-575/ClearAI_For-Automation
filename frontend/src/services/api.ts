/**
 * API service for ClearPath backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://dp-world-hackathon-ocr.web.app/api'

export interface DocumentUploadResponse {
  document_id: string
  filename: string
  document_type: string
  extracted_data: any
  confidence_score: number
  processing_time_ms: number
}

export interface CustomsDeclaration {
  declaration_id: string
  shipper: any
  consignee: any
  items: any[]
  total_value: number
  currency: string
  origin_country: string
  destination_country: string
  hs_codes: string[]
  duty_amount: number
  fta_eligible: boolean
  carbon_footprint: number
  status: string
  errors: any[]
  warnings: any[]
  created_at: string
}

export async function uploadDocument(
  file: File,
  documentType: string
): Promise<DocumentUploadResponse> {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('document_type', documentType)

  const response = await fetch(`${API_BASE_URL}/api/v1/documents/upload`, {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    throw new Error(`Upload failed: ${response.statusText}`)
  }

  return response.json()
}

export async function generateDeclaration(
  documentIds: string[]
): Promise<CustomsDeclaration> {
  const response = await fetch(`${API_BASE_URL}/api/v1/declarations/generate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ document_ids: documentIds }),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Generation failed')
  }

  return response.json()
}

export async function getDeclaration(
  declarationId: string
): Promise<CustomsDeclaration> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/declarations/${declarationId}`
  )

  if (!response.ok) {
    throw new Error('Declaration not found')
  }

  return response.json()
}

export async function getAnalytics(userId: string = 'demo_user'): Promise<any> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/analytics/dashboard?user_id=${userId}`
  )

  if (!response.ok) {
    throw new Error('Failed to fetch analytics')
  }

  return response.json()
}

export async function classifyHSCode(description: string): Promise<any> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/hs-code/classify?description=${encodeURIComponent(description)}`
  )

  if (!response.ok) {
    throw new Error('Classification failed')
  }

  return response.json()
}

export async function calculateCarbon(
  originPort: string,
  destinationPort: string,
  weightKg: number,
  transportMode: string = 'sea'
): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/v1/carbon/calculate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      origin_port: originPort,
      destination_port: destinationPort,
      weight_kg: weightKg,
      transport_mode: transportMode,
    }),
  })

  if (!response.ok) {
    throw new Error('Carbon calculation failed')
  }

  return response.json()
}
