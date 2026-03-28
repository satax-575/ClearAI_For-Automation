import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Download, AlertCircle, CheckCircle, Leaf, FileText, ArrowLeft } from 'lucide-react'
import { getDeclaration } from '../services/api'

export default function ViewDeclaration() {
  const { id } = useParams()
  const [declaration, setDeclaration] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (id) {
      getDeclaration(id)
        .then(setDeclaration)
        .catch(console.error)
        .finally(() => setLoading(false))
    }
  }, [id])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (!declaration) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Declaration Not Found</h2>
        <Link to="/dashboard" className="text-blue-600 hover:underline">
          Return to Dashboard
        </Link>
      </div>
    )
  }

  return (
    <div className="max-w-5xl mx-auto">
      <Link to="/dashboard" className="inline-flex items-center gap-2 text-blue-600 hover:underline mb-6">
        <ArrowLeft className="w-4 h-4" />
        Back to Dashboard
      </Link>

      {/* Header */}
      <div className="bg-white rounded-lg shadow-lg p-8 mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{declaration.declaration_id}</h1>
            <p className="text-gray-600 mt-1">
              {declaration.origin_country} → {declaration.destination_country}
            </p>
          </div>
          <span className={`px-4 py-2 rounded-full font-semibold ${
            declaration.status === 'READY_TO_SUBMIT' 
              ? 'bg-green-100 text-green-800'
              : 'bg-yellow-100 text-yellow-800'
          }`}>
            {declaration.status.replace('_', ' ')}
          </span>
        </div>

        {/* Actions */}
        <div className="flex gap-4">
          <button className="flex items-center gap-2 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition">
            <Download className="w-5 h-5" />
            Download PDF
          </button>
          <button className="flex items-center gap-2 bg-gray-600 text-white px-6 py-3 rounded-lg hover:bg-gray-700 transition">
            <Download className="w-5 h-5" />
            Download XML
          </button>
        </div>
      </div>

      {/* Errors & Warnings */}
      {(declaration.errors.length > 0 || declaration.warnings.length > 0) && (
        <div className="space-y-4 mb-6">
          {declaration.errors.map((error: any, idx: number) => (
            <div key={idx} className="bg-red-50 border-l-4 border-red-500 p-4 rounded">
              <div className="flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-red-500 mt-0.5" />
                <div>
                  <p className="font-semibold text-red-900">{error.field}</p>
                  <p className="text-red-700">{error.message}</p>
                </div>
              </div>
            </div>
          ))}
          
          {declaration.warnings.map((warning: any, idx: number) => (
            <div key={idx} className="bg-yellow-50 border-l-4 border-yellow-500 p-4 rounded">
              <div className="flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-yellow-500 mt-0.5" />
                <div>
                  <p className="font-semibold text-yellow-900">{warning.field}</p>
                  <p className="text-yellow-700">{warning.message}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center gap-3 mb-2">
            <FileText className="w-6 h-6 text-blue-600" />
            <h3 className="font-semibold text-gray-900">Total Value</h3>
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {declaration.currency} {declaration.total_value.toLocaleString()}
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center gap-3 mb-2">
            <CheckCircle className="w-6 h-6 text-green-600" />
            <h3 className="font-semibold text-gray-900">Duty Amount</h3>
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {declaration.currency} {declaration.duty_amount.toLocaleString()}
          </p>
          {declaration.fta_eligible && (
            <p className="text-sm text-green-600 mt-1">FTA Eligible - 0% Duty</p>
          )}
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center gap-3 mb-2">
            <Leaf className="w-6 h-6 text-green-600" />
            <h3 className="font-semibold text-gray-900">Carbon Footprint</h3>
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {declaration.carbon_footprint.toFixed(1)} kg
          </p>
          <p className="text-sm text-gray-600 mt-1">CO₂ equivalent</p>
        </div>
      </div>

      {/* Parties */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold text-gray-900 mb-4">Shipper (Exporter)</h3>
          <div className="space-y-2 text-sm">
            <p><span className="font-medium">Name:</span> {declaration.shipper.name}</p>
            <p><span className="font-medium">Address:</span> {declaration.shipper.address}</p>
            <p><span className="font-medium">Country:</span> {declaration.shipper.country}</p>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold text-gray-900 mb-4">Consignee (Importer)</h3>
          <div className="space-y-2 text-sm">
            <p><span className="font-medium">Name:</span> {declaration.consignee.name}</p>
            <p><span className="font-medium">Address:</span> {declaration.consignee.address}</p>
            <p><span className="font-medium">Country:</span> {declaration.consignee.country}</p>
          </div>
        </div>
      </div>

      {/* Items Table */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="font-semibold text-gray-900 mb-4">Items</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Description</th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">HS Code</th>
                <th className="px-4 py-3 text-right text-sm font-semibold text-gray-900">Quantity</th>
                <th className="px-4 py-3 text-right text-sm font-semibold text-gray-900">Unit Price</th>
                <th className="px-4 py-3 text-right text-sm font-semibold text-gray-900">Total</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {declaration.items.map((item: any, idx: number) => (
                <tr key={idx} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-sm text-gray-900">{item.description}</td>
                  <td className="px-4 py-3 text-sm text-gray-600 font-mono">{item.hs_code}</td>
                  <td className="px-4 py-3 text-sm text-gray-900 text-right">{item.quantity}</td>
                  <td className="px-4 py-3 text-sm text-gray-900 text-right">
                    {declaration.currency} {item.unit_price.toLocaleString()}
                  </td>
                  <td className="px-4 py-3 text-sm font-semibold text-gray-900 text-right">
                    {declaration.currency} {(item.quantity * item.unit_price).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
