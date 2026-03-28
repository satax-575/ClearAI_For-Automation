import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Upload, FileText, CheckCircle, AlertCircle, Loader } from 'lucide-react'
import { uploadDocument, generateDeclaration } from '../services/api'

interface UploadedDoc {
  id: string
  filename: string
  type: string
  status: 'uploading' | 'success' | 'error'
  data?: any
}

export default function UploadDocuments() {
  const navigate = useNavigate()
  const [documents, setDocuments] = useState<UploadedDoc[]>([])
  const [isGenerating, setIsGenerating] = useState(false)

  const handleFileUpload = async (files: FileList | null, docType: string) => {
    if (!files) return

    for (let i = 0; i < files.length; i++) {
      const file = files[i]
      const tempId = `temp-${Date.now()}-${i}`

      // Add to UI immediately
      setDocuments(prev => [...prev, {
        id: tempId,
        filename: file.name,
        type: docType,
        status: 'uploading'
      }])

      try {
        // Upload to backend
        const result = await uploadDocument(file, docType)

        // Update with success
        setDocuments(prev => prev.map(doc =>
          doc.id === tempId
            ? { ...doc, id: result.document_id, status: 'success', data: result }
            : doc
        ))
      } catch (error) {
        // Update with error
        setDocuments(prev => prev.map(doc =>
          doc.id === tempId ? { ...doc, status: 'error' } : doc
        ))
        console.error('Upload failed:', error)
      }
    }
  }

  const handleGenerateDeclaration = async () => {
    const successfulDocs = documents.filter(d => d.status === 'success')
    
    if (successfulDocs.length < 2) {
      alert('Please upload at least Invoice and Packing List')
      return
    }

    setIsGenerating(true)

    try {
      const docIds = successfulDocs.map(d => d.id)
      const declaration = await generateDeclaration(docIds)
      
      // Navigate to declaration view
      navigate(`/declaration/${declaration.declaration_id}`)
    } catch (error) {
      alert('Failed to generate declaration: ' + error)
      console.error(error)
    } finally {
      setIsGenerating(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'uploading':
        return <Loader className="w-5 h-5 animate-spin text-blue-500" />
      case 'success':
        return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-500" />
    }
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-lg shadow-lg p-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Upload Customs Documents
        </h1>
        <p className="text-gray-600 mb-8">
          Upload your trade documents to generate a compliant customs declaration
        </p>

        {/* Upload Sections */}
        <div className="space-y-6">
          {/* Invoice */}
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 hover:border-blue-500 transition">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <FileText className="w-6 h-6 text-blue-600" />
                <div>
                  <h3 className="font-semibold text-gray-900">Commercial Invoice</h3>
                  <p className="text-sm text-gray-500">Required - PDF, JPG, or PNG</p>
                </div>
              </div>
              <label className="cursor-pointer bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition">
                <input
                  type="file"
                  className="hidden"
                  accept=".pdf,.jpg,.jpeg,.png"
                  onChange={(e) => handleFileUpload(e.target.files, 'invoice')}
                />
                Upload
              </label>
            </div>
          </div>

          {/* Packing List */}
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 hover:border-blue-500 transition">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <FileText className="w-6 h-6 text-green-600" />
                <div>
                  <h3 className="font-semibold text-gray-900">Packing List</h3>
                  <p className="text-sm text-gray-500">Required - PDF, JPG, or PNG</p>
                </div>
              </div>
              <label className="cursor-pointer bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition">
                <input
                  type="file"
                  className="hidden"
                  accept=".pdf,.jpg,.jpeg,.png"
                  onChange={(e) => handleFileUpload(e.target.files, 'packing_list')}
                />
                Upload
              </label>
            </div>
          </div>

          {/* Bill of Lading */}
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 hover:border-blue-500 transition">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <FileText className="w-6 h-6 text-purple-600" />
                <div>
                  <h3 className="font-semibold text-gray-900">Bill of Lading</h3>
                  <p className="text-sm text-gray-500">Optional - PDF, JPG, or PNG</p>
                </div>
              </div>
              <label className="cursor-pointer bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition">
                <input
                  type="file"
                  className="hidden"
                  accept=".pdf,.jpg,.jpeg,.png"
                  onChange={(e) => handleFileUpload(e.target.files, 'bill_of_lading')}
                />
                Upload
              </label>
            </div>
          </div>

          {/* Certificate of Origin */}
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 hover:border-blue-500 transition">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <FileText className="w-6 h-6 text-orange-600" />
                <div>
                  <h3 className="font-semibold text-gray-900">Certificate of Origin</h3>
                  <p className="text-sm text-gray-500">Optional - PDF, JPG, or PNG</p>
                </div>
              </div>
              <label className="cursor-pointer bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700 transition">
                <input
                  type="file"
                  className="hidden"
                  accept=".pdf,.jpg,.jpeg,.png"
                  onChange={(e) => handleFileUpload(e.target.files, 'certificate_of_origin')}
                />
                Upload
              </label>
            </div>
          </div>
        </div>

        {/* Uploaded Documents List */}
        {documents.length > 0 && (
          <div className="mt-8">
            <h3 className="font-semibold text-gray-900 mb-4">Uploaded Documents</h3>
            <div className="space-y-2">
              {documents.map((doc) => (
                <div
                  key={doc.id}
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    {getStatusIcon(doc.status)}
                    <div>
                      <p className="font-medium text-gray-900">{doc.filename}</p>
                      <p className="text-sm text-gray-500 capitalize">
                        {doc.type.replace('_', ' ')}
                      </p>
                    </div>
                  </div>
                  {doc.data && (
                    <span className="text-sm text-gray-600">
                      Confidence: {(doc.data.confidence_score * 100).toFixed(0)}%
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Generate Button */}
        {documents.filter(d => d.status === 'success').length >= 2 && (
          <div className="mt-8">
            <button
              onClick={handleGenerateDeclaration}
              disabled={isGenerating}
              className="w-full bg-blue-600 text-white py-4 rounded-lg font-semibold hover:bg-blue-700 transition disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isGenerating ? (
                <>
                  <Loader className="w-5 h-5 animate-spin" />
                  Generating Declaration...
                </>
              ) : (
                <>
                  <Upload className="w-5 h-5" />
                  Generate Customs Declaration
                </>
              )}
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
